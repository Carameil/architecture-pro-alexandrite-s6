import os
from fastapi import FastAPI

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


def configure_tracing() -> None:
    service_name = os.getenv("OTEL_SERVICE_NAME", "service-b")
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://simplest-collector.observability:4317")
    exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)


configure_tracing()

app = FastAPI()
FastAPIInstrumentor().instrument_app(app)


@app.get("/")
async def root():
    return "service-b ok"


