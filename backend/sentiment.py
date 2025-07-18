import os
import logging
import asyncio
import time
from threading import Lock, Thread
from queue import Queue, Empty
from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TFAutoModelForSequenceClassification
)
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ModelChangeHandler(FileSystemEventHandler):
    def __init__(self, analyzer_instance):
        self.analyzer = analyzer_instance
        self.last_reload_time = 0
        self.reload_cooldown = 2.0

    def on_modified(self, event):
        if not event.is_directory:
            model_files = ["pytorch_model.bin", "tf_model.h5", "config.json", "tokenizer.json", "tokenizer_config.json"]
            if any(model_file in event.src_path for model_file in model_files):
                current_time = time.time()
                if current_time - self.last_reload_time > self.reload_cooldown:
                    logger.info(f"Detected modification in model file: {event.src_path}. Triggering model reload.")
                    self.last_reload_time = current_time
                    time.sleep(0.5)
                    self.analyzer.load_model()

    def on_created(self, event):
        self.on_modified(event)

class RequestBatcher:
    def __init__(self, predict_func, batch_size=8, max_latency_ms=50):
        self.predict_func = predict_func
        self.batch_size = batch_size
        self.max_latency = max_latency_ms / 1000.0
        self.queue = Queue()
        self.worker_thread = Thread(target=self._batch_worker, daemon=True)
        self.worker_thread.start()

    async def submit(self, text):
        """Submits a request to the batcher and waits for the result."""
        future = asyncio.Future()
        self.queue.put((text, future))
        return await future

    def _batch_worker(self):
        """The background worker that creates and processes batches."""
        while True:
            items = []
            try:
                items.append(self.queue.get(timeout=self.max_latency))
            except Empty:
                continue

            while len(items) < self.batch_size:
                try:
                    items.append(self.queue.get(timeout=self.max_latency))
                except Empty:
                    break

            texts = [text for text, future in items]
            futures = [future for text, future in items]

            try:
                results = self.predict_func(texts)
                for future, result in zip(futures, results):
                    future.set_result(result)
            except Exception as e:
                logger.error(f"Error processing batch: {e}", exc_info=True)
                for future in futures:
                    future.set_exception(e)


class SentimentAnalyzer:
    def __init__(self):
        self.model_name = os.environ.get("MODEL_NAME", "distilbert-base-uncased-finetuned-sst-2-english")
        self.framework = os.environ.get("FRAMEWORK", "pt").lower()
        self.model_path = "./model"
        self.pipeline = None
        self.load_lock = Lock()
        self.batcher = RequestBatcher(self._predict_batch)
        self.observer = None

        self.load_model()
        self._start_watcher()

    def load_model(self):
        with self.load_lock:
            try:
                model_class = AutoModelForSequenceClassification if self.framework == 'pt' else TFAutoModelForSequenceClassification
                model_file = "pytorch_model.bin" if self.framework == 'pt' else "tf_model.h5"

                if os.path.exists(self.model_path) and os.path.exists(os.path.join(self.model_path, model_file)):
                    logger.info(f"Loading fine-tuned {self.framework} model from {self.model_path}")
                    tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                    model = model_class.from_pretrained(self.model_path)
                else:
                    logger.info(f"Loading pre-trained {self.framework} model: {self.model_name}")
                    tokenizer = AutoTokenizer.from_pretrained(self.model_name)

                    if self.framework == 'tf' and os.path.exists(os.path.join(self.model_path, "pytorch_model.bin")):
                        model = model_class.from_pretrained(self.model_name, from_pt=True)
                    else:
                        model = model_class.from_pretrained(self.model_name)

                if self.pipeline is not None:
                    del self.pipeline

                self.pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer, framework=self.framework)
                logger.info(f"Successfully loaded {self.framework} model.")

            except Exception as e:
                logger.error(f"Error loading model: {e}", exc_info=True)
                if self.pipeline is None:
                    raise

    def _predict_batch(self, texts: list[str]):
        if self.pipeline is None:
            raise RuntimeError("Model is not loaded.")
        
        with self.load_lock:
            try:
                results = self.pipeline(texts)
                return [
                    {"label": "positive" if res["label"].upper() == "POSITIVE" else "negative", "score": float(res["score"])}
                    for res in results
                ]
            except Exception as e:
                logger.error(f"Batch prediction error: {e}", exc_info=True)
                raise

    async def predict(self, text: str):
        return await self.batcher.submit(text)

    def _start_watcher(self):
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
            
        event_handler = ModelChangeHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.model_path, recursive=True)
        self.observer.daemon = True
        self.observer.start()
        logger.info(f"Started watching directory for model changes: {self.model_path}")

    def stop_watcher(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Stopped file watcher")

    def __del__(self):
        self.stop_watcher()