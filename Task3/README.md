# Task3.1 — OpenTelemetry + Jaeger (Kubernetes MVP)

Ниже — команды «с нуля», чтобы поднять Jaeger, задеплоить 2 Python‑сервиса (`service-a` → вызывает `service-b`), проверить трейс и остановить кластер.

## Требования
- Minikube, kubectl, Docker

## Развёртывание

1) Старт Minikube
```bash
minikube start --addons=ingress
```

2) Установить cert-manager (нужен Jaeger Operator) и дождаться готовности
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml
kubectl -n cert-manager wait --for=condition=Available --timeout=300s \
  deploy/cert-manager deploy/cert-manager-webhook deploy/cert-manager-cainjector
```

3) Установить Jaeger Operator и развернуть Jaeger all‑in‑one
```bash
kubectl create namespace observability
kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.51.0/jaeger-operator.yaml -n observability
kubectl -n observability wait --for=condition=Available --timeout=300s deploy/jaeger-operator

# CR уже содержит namespace: observability
kubectl apply -f k8s/jaeger-instance.yaml
kubectl -n observability get pods,svc | grep simplest
```
Ожидаем сервисы: `simplest-collector` (4317/4318), `simplest-query` (16686).

4) Сборка образов сервисов внутри Minikube
```bash
minikube image build -t service-a:latest services/service-a/
minikube image build -t service-b:latest services/service-b/
```

5) Деплой сервисов и ожидание готовности
```bash
kubectl apply -f k8s/services.yaml
kubectl get pods -w   # дождаться статус Running, затем Ctrl+C
```

## Проверка трассировки

1) Сгенерировать трафик (service-a вызывает service-b)
```bash
kubectl run curl --image=curlimages/curl:8.10.0 --rm -it --restart=Never -- \
  curl -s http://service-a:8080
```
Альтернатива (в контейнерах есть wget):
```bash
kubectl exec -it $(kubectl get pods -l app=service-a -o jsonpath={.items[0].metadata.name}) -- \
  wget -qO- http://service-a:8080
```

2) Открыть Jaeger UI
```bash
kubectl -n observability port-forward svc/simplest-query 16686:16686
# браузер: http://localhost:16686 → Service: service-a → Find Traces
```
Ожидается один трейс с двумя сервисами: `service-a` (GET /) и вложенные спаны `service-b`.

## Остановка
```bash
minikube stop
```

## Полезно для диагностики
```bash
# проверить env с адресом OTLP gRPC (4317)
kubectl get deploy service-a -o yaml | grep -A2 OTEL_EXPORTER_OTLP_ENDPOINT
kubectl get deploy service-b -o yaml | grep -A2 OTEL_EXPORTER_OTLP_ENDPOINT

# логи приложений
kubectl logs deploy/service-a
kubectl logs deploy/service-b

# проверить Jaeger сервисы
a="observability"; kubectl -n $a get pods,svc | grep simplest
```

Примечание: сервисы переписаны на Python FastAPI + OpenTelemetry (OTLP gRPC). Файлы `package.json` не требуются.
