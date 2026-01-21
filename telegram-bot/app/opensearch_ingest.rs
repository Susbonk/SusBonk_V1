use std::{sync::Arc, time::Duration};

use chrono::{SecondsFormat, Utc};
use serde_json::{json, Map, Value};
use tokio::{
    sync::{mpsc, oneshot},
    task::JoinHandle,
    time,
};
use tracing::{Event, Subscriber};
use tracing_core::Field;
use tracing_subscriber::{
    layer::{Context, Layer},
    registry::LookupSpan,
};

#[derive(Clone)]
pub struct OpenSearchIngestLayer {
    tx: mpsc::Sender<Value>,
    service_name: Arc<String>,
    extra_fields: Arc<Map<String, Value>>,
}

pub struct OpenSearchIngestHandle {
    stop_tx: Option<oneshot::Sender<()>>,
    task: JoinHandle<()>,
}

impl OpenSearchIngestHandle {
    pub async fn shutdown(mut self) {
        if let Some(tx) = self.stop_tx.take() {
            let _ = tx.send(());
        }
        let _ = self.task.await;
    }
}

pub struct OpenSearchIngestConfig {
    pub ingest_url: String,               // e.g. http://localhost:8080/ingest
    pub service_name: String,             // e.g. "telegram-bot"
    pub batch_size: usize,                // e.g. 200
    pub flush_interval: Duration,         // e.g. 1s
    pub max_queue: usize,                 // e.g. 10_000
    pub extra_fields: Map<String, Value>, // merged into "fields"
    pub headers: Vec<(String, String)>,   // optional HTTP headers
}

impl Default for OpenSearchIngestConfig {
    fn default() -> Self {
        Self {
            ingest_url: "http://localhost:8080/ingest".to_string(),
            service_name: "telegram-bot".to_string(),
            batch_size: 200,
            flush_interval: Duration::from_secs(1),
            max_queue: 10_000,
            extra_fields: Map::new(),
            headers: vec![],
        }
    }
}

pub fn opensearch_ingest_layer(
    cfg: OpenSearchIngestConfig,
) -> (OpenSearchIngestLayer, OpenSearchIngestHandle) {
    let service_name = Arc::new(cfg.service_name);
    let extra_fields = Arc::new(cfg.extra_fields);

    let (tx, mut rx) = mpsc::channel::<Value>(cfg.max_queue);
    let (stop_tx, mut stop_rx) = oneshot::channel::<()>();

    let ingest_url = cfg.ingest_url;
    let batch_size = cfg.batch_size;
    let flush_interval = cfg.flush_interval;

    // HTTP client
    let mut headers = reqwest::header::HeaderMap::new();
    for (k, v) in cfg.headers {
        if let (Ok(name), Ok(value)) = (
            reqwest::header::HeaderName::from_bytes(k.as_bytes()),
            reqwest::header::HeaderValue::from_str(&v),
        ) {
            headers.insert(name, value);
        }
    }

    let client = reqwest::Client::builder()
        .default_headers(headers)
        .build()
        .expect("reqwest client build");

    let task = tokio::spawn(async move {
        let mut buf: Vec<Value> = Vec::with_capacity(batch_size);
        let mut ticker = time::interval(flush_interval);
        ticker.set_missed_tick_behavior(time::MissedTickBehavior::Delay);

        let mut stopped = false;

        loop {
            tokio::select! {
                _ = &mut stop_rx, if !stopped => {
                    stopped = true;
                }

                _ = ticker.tick() => {
                    if !buf.is_empty() {
                        flush_batch(&client, &ingest_url, &mut buf).await;
                    }
                    if stopped {
                        drain_all(&mut rx, &mut buf, batch_size, &client, &ingest_url).await;
                        break;
                    }
                }

                msg = rx.recv() => {
                    match msg {
                        Some(ev) => {
                            buf.push(ev);
                            if buf.len() >= batch_size {
                                flush_batch(&client, &ingest_url, &mut buf).await;
                            }
                        }
                        None => {
                            if !buf.is_empty() {
                                flush_batch(&client, &ingest_url, &mut buf).await;
                            }
                            break;
                        }
                    }
                }
            }
        }
    });

    let layer = OpenSearchIngestLayer {
        tx,
        service_name,
        extra_fields,
    };

    let handle = OpenSearchIngestHandle {
        stop_tx: Some(stop_tx),
        task,
    };

    (layer, handle)
}

impl<S> Layer<S> for OpenSearchIngestLayer
where
    S: Subscriber + for<'a> LookupSpan<'a>,
{
    fn on_event(&self, event: &Event<'_>, ctx: Context<'_, S>) {
        // sync: only try_send. If queue is full -> drop.
        let meta = event.metadata();

        // Start with configured extra fields
        let mut fields = Map::<String, Value>::new();
        for (k, v) in self.extra_fields.iter() {
            fields.insert(k.clone(), v.clone());
        }

        // Add event fields
        event.record(&mut JsonVisitor(&mut fields));

        // Standard-ish useful meta
        fields.insert("logger".to_string(), Value::String(meta.target().to_string()));

        // Span context (minimal)
        let mut span_fields = Map::<String, Value>::new();
        if let Some(span) = ctx.lookup_current() {
            span_fields.insert("name".to_string(), Value::String(span.name().to_string()));
        }

        let message = fields
            .get("message")
            .and_then(|v| v.as_str())
            .or_else(|| fields.get("msg").and_then(|v| v.as_str()))
            .unwrap_or("")
            .to_string();

        let mut event_obj = json!({
            "@timestamp": iso8601_utc_now(),
            "service": { "name": self.service_name.as_str() },
            "log": { "level": meta.level().to_string() },
            "message": message,
            "fields": fields,
        });

        if !span_fields.is_empty() {
            event_obj["span"] = Value::Object(span_fields);
        }

        let _ = self.tx.try_send(event_obj);
    }
}

struct JsonVisitor<'a>(&'a mut Map<String, Value>);

impl<'a> tracing::field::Visit for JsonVisitor<'a> {
    fn record_i64(&mut self, field: &Field, value: i64) {
        self.0.insert(field.name().to_string(), Value::Number(value.into()));
    }
    fn record_u64(&mut self, field: &Field, value: u64) {
        self.0.insert(field.name().to_string(), Value::Number(value.into()));
    }
    fn record_bool(&mut self, field: &Field, value: bool) {
        self.0.insert(field.name().to_string(), Value::Bool(value));
    }
    fn record_str(&mut self, field: &Field, value: &str) {
        self.0.insert(field.name().to_string(), Value::String(value.to_string()));
    }
    fn record_error(&mut self, field: &Field, value: &(dyn std::error::Error + 'static)) {
        self.0
            .insert(field.name().to_string(), Value::String(value.to_string()));
    }
    fn record_debug(&mut self, field: &Field, value: &dyn std::fmt::Debug) {
        self.0.insert(
            field.name().to_string(),
            Value::String(format!("{value:?}")),
        );
    }
}

fn iso8601_utc_now() -> String {
    Utc::now().to_rfc3339_opts(SecondsFormat::Millis, true)
}

async fn drain_all(
    rx: &mut mpsc::Receiver<Value>,
    buf: &mut Vec<Value>,
    batch_size: usize,
    client: &reqwest::Client,
    url: &str,
) {
    while let Ok(ev) = rx.try_recv() {
        buf.push(ev);
        if buf.len() >= batch_size {
            flush_batch(client, url, buf).await;
        }
    }
    if !buf.is_empty() {
        flush_batch(client, url, buf).await;
    }
}

async fn flush_batch(client: &reqwest::Client, url: &str, buf: &mut Vec<Value>) {
    // best-effort: no retry, no panic, no tracing logs here
    let payload = std::mem::take(buf);
    let res = client.post(url).json(&payload).send().await;
    if let Ok(r) = res {
        if r.status().as_u16() >= 400 {
            let _ = r.text().await;
        }
    }
}
