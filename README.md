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
