# Containerization and  Orchestration

## Lab 1

[LLM-based story generation service](/lab1/)

* Base model: [TinyLlama2-110M](https://huggingface.co/nickypro/tinyllama-110M)
* Interface: streamlit
  * Local URL: <http://localhost:8501>
  * Network URL: <http://172.17.0.2:8501>
  * External URL: <http://178.178.245.34:8501>
* Inference: CPU only
* Saving chat history (as Docker Volume `/app/data`)

![Lab 1 demo](/media/storygen1.gif)

### Structure

```tree
└── lab1
    ├── bad.Dockerfile
    ├── chat_data
    │   └── chat_history.json
    ├── good.Dockerfile
    ├── requirements.txt
    └── storyteller
        ├── app.py
        ├── model.py
        └── preload.py
```

### How to run

#### Set up

```cmd
git clone git@github.com:deniskirbaba/containerization-orchestration.git
cd lab1
```

#### Build

```cmd
docker build -t storyteller_image -f good.Dockerfile ./
```

#### Run

```cmd
docker run -d \
    -p 8501:8501 \
    -v $(pwd)/chat_data:/app/data \
    --name storyteller_app storyteller_image
```

#### Stop and restart

```cmd
docker stop storyteller_app
docker start storyteller_app
```

### Dockerfiles

["Bad" Dockerfile](/lab1/bad.Dockerfile)

["Good" Dockerfile](/lab1/good.Dockerfile)

#### Bad practices

1. `FROM python:3.12`. Версии базовых образов надо строго определять (так же как и версии библиотек в `requirements.txt`), так как иначе они каждый раз будут стягиваться по-новой и возможна ситуация когда у нас не будет совместимости через некоторое время. Также можно использовать slim версии (если это возможно) чтобы уменьшить размер контейнера за счёт удаления ненужных библиотек и инструментов.
    * Размер "good" контейнера - 1.94GB
    * Размер "bad" контейнера - 2.84GB
2. `COPY . .` и затем сразу `RUN pip install -r requirements.txt`. Тут 2 проблемы:
    1. Нет разделения на установку системных зависимостей и питоновских зависимостей сервиса. Это важно, так как некоторые (а в этом случае numpy, pandas, torch) пакеты Python требуют системных библиотек, например `gcc, g++` для компиляции. Разделение позволяет избежать ошибок из-за их устаревания/отсутствия.
    2. Более важно то, что таким образом у нас установка всех зависимостей в одном Docker слое, а это плохо, так как выше у нас еще и `COPY . .`. То есть при любых изменениях в коде у нас будет пересобираться этот слой и это будет занимать очень много времени так как кэширование слоёв не будет использоваться должным образом.

    Поэтому логичнее разделить эти два слоя на следующие слои:  установка системных зависимостей, копирование только файла с сервисными зависимостями, установка сервисных зависимостей, копирование всех остальных файлов сервиса.  
3. Не указывать `EXPORT`, `VOLUME`. Эти команды являются чисто "документационными", однако их опускать не стоит, так как они дают возможность разработчикам быстрее разобраться с докеризованным приложением.
4. Игнорирование Python оптимизаций:
    1. `PIP_NO_CACHE_DIR=on` - отключает кэш при установке библиотек - уменьшаем размер образа.
    2. `PYTHONUNBUFFERED=1` - отключает буфер для stdout, stderr - максимально быстрое получение информации от запущенного приложения в логи контейнера + в случае сбоя сразу увидим ошибку.
    3. ...

#### Когда не стоит использовать "good" контейнер

1. Нужна максимальная производительность. Например в DL, когда мы хотим по-максимуму утилизировать вычислительные ресурсы машины добавление Docker Engine в качестве уровня абстракции может привести к дополнительным затратам мощностей из-за виртуализации. То есть если я захочу добавить LLM в этот сервис, которая будет потреблять почти все ресурсы моей машины, то лучше развертывать приложение непосредственно на "голом" металле.
2. Обучение новых моделей или адаптация архитектур. Этот контейнер оптимизирован для выводов с использованием предварительно загруженных весов модели (`storyteller/preload.py`). Если потребуется немного изменить архитектуру (н-р добавить LoRA) то такой настройки контейнера может быть недостаточно. Так как будут требоваться другие зависимости, библиотеки.

#### Когда не стоит использовать контейнеры в целом

1. Этап разработки или отладки ML решений. На ранних этапах разработки или экспериментов требуется частое изменение кода. И перестраивать и перезапускать контейнеры после каждого изменения может сильно замедлить разработку, так как как правило число зависимостей очень большое. Наверно лучше на этом этапе использовать только Conda, а контейнеры только на этапе развертывания.

2. Требования low latency в NLP. Контейнерная среда будет добавлять задержку. Поэтому лучше использовать специализированные инструменты, которые оптимизированы под DL (например NVIDIA TensorRT).

## Lab 2

[LLM-based story generation service - 2](/lab2/)

* Base model: [TinyLlama2-110M](https://huggingface.co/deniskirbaba/tinyllama-110M-F16-GGUF)
* Interface: streamlit
  * Local URL: <http://localhost:8501>
  * Network URL: <http://172.17.0.2:8501>
  * External URL: <http://178.178.245.34:8501>
* Inference: via llama.cpp, CPU only
  * Streaming mode for story generation
  * Simple web front end to interact with llama.cpp: <http://localhost:8080>, but my service use streamlit-based front end
* Init container `loader` for loading HF model in GGUF format and save as Docker Volume `/models`
* Chat history
  * PostgreSQL
  * Data dumps are saved as Docker Volume `/chat_history`

![Lab 2 demo](/media/storygen2.gif)

### Structure

```cmd
└── lab2
    ├── app
    │   ├── app.py
    │   ├── database
    │   │   ├── connection.py
    │   │   ├── datamodel.py
    │   │   └── __init__.py
    │   ├── database_bridge.py
    │   ├── Dockerfile
    │   ├── model_bridge.py
    │   └── requirements.txt
    ├── loader
    │   ├── Dockerfile
    │   └── load.sh
    ├── docker-compose.yml
    ├── models
    └── postgres_data
```

### Services

[docker-compose](/lab2/docker-compose.yml)

#### [Loader (init container)](/lab2/loader/)

Проверяет наличие весов модели на локальной машине (Volume `/models`), при отсутствии загружает их с Hugging Face.

#### [Model server llama.cpp](https://github.com/ggerganov/llama.cpp)

Сервер для эффективного инференса LLM на CPU с минимальными зависимостями. Используется Docker образ (`ghcr.io/ggerganov/llama.cpp:server`).

* Предлагает интерфейс для взаимодействия с моделью на <http://localhost:8080>, однако данный сервис использует интерфейс на streamlit <http://localhost:8501>.
* Docker Volume для хранения моделей
* healthcheck для проверки готовности сервера (проверка осуществляется запросом на <http::/localhost:8080/health> - [info](https://github.com/ggerganov/llama.cpp/blob/master/examples/server/README.md#get-health-returns-heath-check-result))
* Запрос на генерацию текста нужно подавать в виде POST запроса на <http://localhost:8080/completion> - [info](https://github.com/ggerganov/llama.cpp/blob/master/examples/server/README.md#post-completion-given-a-prompt-it-returns-the-predicted-completion)

#### DB PostgreSQL

PostgreSQL DB на основе образа `postgres:17.2-alpine3.20`. Креды БД находятся в файле [.env](/lab2/.env). Реализован healthcheck, а также сохранение данных через Docker Volumes в папку [postgres_data](/lab2/postgres_data/) (поставлено ограничение в 128mb).

#### [Application](/lab2/storyteller/)

Основное приложение - реализует логику, отправляет запросы на генерацию к серверу llama.cpp, сохраняет данные о переписке в БД, реализует интерфейс через Streamlit.

Зависит от двух сервисов: база данных и сервер llama.cpp. Будет работать только в случае их исправности.

### Questions

#### Можно ли ограничивать ресурсы (например, память или CPU) для сервисов в docker-compose.yml? Если нет, то почему, если да, то как?

[Да, можно](https://docs.docker.com/reference/compose-file/deploy/#resources). У каждого сервиса можно прописать ключ `deploy`, а в нем ключ `resources`. В нем можно указать как ограничения `limits` (верхнюю планку), так и нижнюю планку `reservations`. Можно конфигурировать:

* CPU, GPU, TPU
* Память
* Лимит на число процессов

Например:

```yml
services:
  model:
    image: llama3
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 500M
          pids: 10
        reservations:
          cpus: '0.25'
          memory: 200M
          devices:
            - capabilities: ["nvidia-compute"]
              driver: nvidia
```

#### Как можно запустить только определенный сервис из docker-compose.yml, не запуская остальные?

Да, нужно выполнить не `up`, а `start` команду и прописать имя сервиса. Например:

```cmd
docker compose start model
```

## Lab 3

Манифесты из вводной части находятся в [original_manifests](/lab3/original_manifests/), манифесты из задания находятся в [edited_manifests](/lab3/edited_manifests/).

**Структура**:

```cmd
lab3
├── edited_manifests
│   ├── nextcloud_configmap.yml
│   ├── nextcloud_secret.yml
│   ├── nextcloud.yml
│   ├── postgres_configmap.yml
│   ├── postgres_deployment.yml
│   ├── postgres_secret.yml
│   └── postgres_service.yml
└── original_manifests
    ├── nextcloud.yml
    ├── pg_configmap.yml
    ├── pg_deployment.yml
    └── pg_service.yml
```

### Tutorials

> **Вопрос: важен ли порядок выполнения этих манифестов? Почему?**  
Если манифесты зависят друг от друга (как в случае с `pg_configmap.yml`, `pg_service.yml`, `pg_deployment.yml`), то порядок важен. Так как например если вначале запустить `pg_deployment.yml`, то контейнер с postgres не сможет запуститься без кредов БД (которые передаются в `pg_configmap.yml`).
![pg_deployment is down](/media/lab3-1.png)
Также, если запустить `pg_service.yml` после `pg_deployment.yml`, то сущность service для пода postgres не будет определена, а значит не будет уникального постоянного IP вне жизненного цикла поды postgres и мы не сможем потом взаимодействовать с БД извне кластера.  
То есть, вообще говоря нет смысла так делать, так как в любом случае наш сервис будет недоступен до тех пор, пока не будут запущены требуемые манифесты без которых невозможна нормальная работа.

![k8s dashboard](/media/lab%203-2.png)

> **Вопрос: что (и почему) произойдет, если отскейлить количество реплик postgres-deployment в 0,
затем обратно в 1, после чего попробовать снова зайти на Nextcloud?**  
При уменьшении реплик postgres в 0 - мы просто убиваем все наши экземпляры БДшки - из-за этого нода Nextcloud теряет соединение и остаётся висеть без него. КОгда мы заново запускаем реплику - БДшка встанет, однако nextcloud уже не будет переподключаться к ней (она бы переподключилась если бы тоже упала, но такого не происходит).

### Task

1. Перенесеты креды (user и password) для postgres в отдельный манифест [postgres_secrets.yml](/lab3/edited_manifests/postgres_secrets.yml).

2. Перенесеты переменные окружения для nextcloud в [nextcloud_configmap.yml](/lab3/edited_manifests/nextcloud_configmap.yml), а также креды вынесены в отдельный манифест [nextcloud_scret.yml](/lab3/edited_manifests/nextcloud_secret.yml).

3. Добавлены readyness и liveness проверки ([nextcloud.yml](/lab3/edited_manifests/nextcloud.yml)). Исходя из информации из документации kubernetes:

    > A common pattern for liveness probes is to use the same low-cost HTTP endpoint as for readiness probes, but with a higher failureThreshold. This ensures that the pod is observed as not-ready for some period of time before it is hard killed.

    То есть по сути readyness проба определяет статус, при котором контейнер готов принимать входящий трафик и это необходимо когда контейнеру нужно время на загрузку, установку конфигурации или скачивание файлов. А liveness проба определяет когда перезапускать контейнер, если он вдруг стал работать нестабильно.

![edited dashboard](/media/lab%203-3.png)

### Screenshots

![minikube start](/media/lab3-4.png)

![config](/media/lab3-5.png)

![creating manifests](/media/lab3-6.png)

![check entites](/media/lab3-7.png)

![describe nextcloud](/media/lab3-8.png)

![describe postgres](/media/lab3-9.png)

![nextcloud](/media/lab3-10.png)

![another dashboard](/media/lab3-11.png)

## Lab 4

### Description

Service for detecting emotions from text:

* ML Task: multi-label text classification
* Model: [SamLowe/roberta-base-go_emotions](https://huggingface.co/SamLowe/roberta-base-go_emotions) 
* The system is divided into 2 parts:
  1. Gradio interface
  2. Model server - FastAPI and pure Pipeline class from HF
* Interaction via HTTP

#### Demo

![emotion-prediction-demo](/media/lab4-demo-gif.gif)

### Structure

```cmd
└── lab4
    ├── interface
    │   ├── Dockerfile
    │   └── src
    │       ├── emotions.py
    │       ├── interface.py
    │       └── requirements.txt
    ├── kubernetes_manifests
    │   ├── interface_configmap.yml
    │   ├── interface_deployment.yml
    │   ├── interface_service.yml
    │   ├── predict_emotions_deployment.yml
    │   └── predict_emotions_service.yml
    ├── model-loader
    │   ├── Dockerfile
    │   └── load-model.sh
    └── predict-emotions
        ├── Dockerfile
        └── src
            ├── api.py
            ├── model.py
            └── requirements.txt
```

### Services

#### [Interface](/lab4/interface/)

Realizes web frontend using Gradio. Sends requests entered into the form to the model server, processes the response and transforms the data for convenient visualization.

Build docker image:

```cmd
cd lab4/interface
docker build -t cont-lab4-interface -f Dockerfile ./src
```

#### [Model loader (initContainer)](/lab4/model-loader/)

Init-container that implements one-time loading of model and tokenizer from HF. Saves this data to volume.

Build docker image:

```cmd
cd lab4/model-loader
docker build -t cont-lab4-load-model -f Dockerfile .
```

#### [Predict emotions](/lab4/predict-emotions/)

A microservice that accepts text queries (/predict) and returns emotions predict results as a list of different emotions and their probabilities. Loads the model and tokenizer from a local folder to be mounted to the service.

There are also API `/health` for livenessProbe.

Build docker image:

```cmd
cd lab4/predict-emotions
docker build -t cont-lab4-predict-emotions -f Dockerfile ./src
```

### [Manifests](/lab4/kubernetes_manifests/)

#### Interface

* [deployment](/lab4/kubernetes_manifests/interface_deployment.yml) - describes the `deployment` of the interface. Ports for services are defined, and environment variables (for interface configuration) are passed from the
 [interface_configmap](/lab4/kubernetes_manifests/interface_configmap.yml)
* [configmap](/lab4/kubernetes_manifests/interface_configmap.yml) - defining environment variables for interface configuration
* [service](/lab4/kubernetes_manifests/interface_service.yml) - defining a `service` entity of the `NodePort` type to make communication between pods convenient, as well as for further access outside of the cluster

#### Predict emotions

* [deployment](/lab4/kubernetes_manifests/predict_emotions_deployment.yml) - definition of the `deployment` entity for model server. The port on which the service will run is defined. Created an `emptyDir` (ephemeral volume) to store the model and tokenizer, and then this volume is mounted to `initContainer` (which loads this data) and the model server itself (which uses the model). Also implemented `livenessProbe` of `httpGet` type - which checks if the container is healthy by analyzing the status codes of the response (if 200-399 - it is healthy)
* [service](/lab4/kubernetes_manifests/predict_emotions_service.yml) - defining a `service` entity of the `NodePort` type to make communication between pods convenient, as well as for further access outside of the cluster

### Launching cluster

Starting minikube:

```cmd
minikube start
```

In order to use local Docker images in Minikube, execute this in every terminal, which will be used for cluster manipulating:

```cmd
eval $(minikube docker-env)
```

Also need to build docker images after executing this command!  
Thanks this [stackoverflow post](https://stackoverflow.com/questions/42564058/how-can-i-use-local-docker-images-with-minikube)

So, when listing all Docker images we can see this:
![docker images](/media/lab4-1.png)

Applying all manifests:

```cmd
kubectl apply -f interface_configmap.yml &&
kubectl apply -f interface_service.yml &&
kubectl apply -f interface_deployment.yml &&
kubectl apply -f predict_emotions_service.yml &&
kubectl apply -f predict_emotions_deployment.yml
```

So, when introspecting entities, we can see this:
![get entities](/media/lab4-2.png)

Also, can see some logs:

```cmd
kubectl logs -f interface-6598dc58f8-9x4wp
```

![interface logs](/media/lab4-3.png)

From logs of predict-emotions service we can see the HTTP liveness checks:

```cmd
kubectl logs -f predict-emotions-594889d556-cbzr7
```

![predict logs](/media/lab4-4.png)

For getting access from outside of the cluster to the interface we need to `port-forward` ports. (Note: on my PC `minikube service <service-name>` command don't work - [github issue](https://github.com/kubernetes/minikube/issues/13746)).

```cmd
kubectl port-forward service/interface-service 8080:8080
```

After that, we are able to open interface at `localhost:8080`:
![iterface](/media/lab4-5.png)
