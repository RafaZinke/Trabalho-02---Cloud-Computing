#  Fórum Online - Aplicação Multicontainer

> **Trabalho 02 - Cloud Computing**
> UNIDAVI - Sistemas de Informação
> Prof. Esp. Ademar Perfoll Junior

---

##  Descrição da Aplicação

Esta aplicação simula a infraestrutura de um **Fórum Online**, onde usuários podem se cadastrar, criar tópicos de discussão em diferentes categorias e responder a outros tópicos. O projeto foi totalmente conteinerizado utilizando **Docker** e **Docker Compose**, simulando um ambiente real de Cloud Computing com múltiplos containers conectados.

A aplicação realiza operações **CRUD** completas sobre dois tipos de entidades principais (usuários e tópicos), além de respostas, persistindo todos os dados em um banco PostgreSQL rodando em container separado, com volume Docker para garantir a persistência mesmo após reinicializações.



## Tecnologias Utilizadas

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.12 + Flask 3.0 |
| Servidor WSGI | Gunicorn |
| Driver de Banco | psycopg2-binary |
| Banco de Dados | PostgreSQL 16 (Alpine) |
| Frontend | HTML5 + CSS3 + Jinja2 |
| Containerização | Docker + Docker Compose |
| Registry | DockerHub |

---

## Arquitetura

```
┌────────────────────────────────────────────────────────────┐
│                       Máquina Host                         │
│                                                            │
│   ┌────────────────────────────────────────────────────┐   │
│   │              Rede Docker: forum_net                │   │
│   │                                                    │   │
│   │  ┌──────────────────┐      ┌──────────────────┐    │   │
│   │  │  Container app   │ ───► │  Container db    │    │   │
│   │  │  (forum_app)     │      │  (forum_db)      │    │   │
│   │  │                  │      │                  │    │   │
│   │  │  Flask + Gunicorn│      │  PostgreSQL 16   │    │   │
│   │  │  Porta 5000      │      │  Porta 5432      │    │   │
│   │  └────────┬─────────┘      └────────┬─────────┘    │   │
│   │           │                         │              │   │
│   └───────────┼─────────────────────────┼──────────────┘   │
│               │                         │                  │
│         localhost:5000             ┌─────▼──────┐          │
│         (navegador)                │   Volume   │          │
│                                    │forum_db_data│         │
│                                    └────────────┘          │
└────────────────────────────────────────────────────────────┘
```

**Componentes:**

1. **forum_app**: Container da aplicação Flask que serve a interface web e o backend.
2. **forum_db**: Container PostgreSQL que armazena todos os dados.
3. **forum_net**: Rede bridge interna que permite a comunicação entre os containers usando DNS interno (`db` como hostname).
4. **forum_db_data**: Volume nomeado do Docker que persiste os dados do PostgreSQL no host.

---

## ⚙ Variáveis de Ambiente

Definidas no arquivo `.env`:

| Variável | Descrição | Valor padrão |
|----------|-----------|--------------|
| `DB_NAME` | Nome do banco de dados | `forumdb` |
| `DB_USER` | Usuário do banco | `forumuser` |
| `DB_PASSWORD` | Senha do banco | `forumpass` |
| `SECRET_KEY` | Chave secreta do Flask | `troque-esta-chave-em-producao` |

Variáveis internas configuradas no `docker-compose.yml`:

| Variável | Valor |
|----------|-------|
| `DB_HOST` | `db` (nome do serviço no Compose) |
| `DB_PORT` | `5432` |

---

## 🔌 Portas Utilizadas

| Serviço | Porta no Container | Porta no Host |
|---------|-------------------|---------------|
| Flask (app) | 5000 | **5000** |
| PostgreSQL (db) | 5432 | 5432 |

Acesso à aplicação: **http://localhost:5000**

---

## Instruções Completas de Execução

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) versão 20.10+
- [Docker Compose](https://docs.docker.com/compose/install/) v2+
- [Git](https://git-scm.com/)

### Passo 1: Clonar o repositório

```bash
git clone https://github.com/RafaZinke/Trabalho-02---Cloud-Computing.git
cd forum-online
```

### Passo 2 (opcional): Ajustar variáveis de ambiente

O arquivo `.env` já está pronto com valores padrão. Se quiser personalizar:

```bash
nano .env
```

### Passo 3: Subir os containers

```bash
docker compose up -d --build
```

Esse comando irá:

1. Construir a imagem da aplicação a partir do `Dockerfile`
2. Baixar a imagem oficial do PostgreSQL 16
3. Criar a rede `forum_net`
4. Criar o volume `forum_db_data`
5. Iniciar os containers `forum_db` e `forum_app`
6. Aguardar o banco ficar saudável (healthcheck)
7. Inicializar automaticamente as tabelas no banco

### Passo 4: Acessar a aplicação

Abra no navegador:

```
http://localhost:5000
```

### Passo 5: Comandos úteis

```bash
# Ver logs em tempo real
docker compose logs -f

# Ver status dos containers
docker compose ps

# Parar os containers (mantém os dados)
docker compose down

# Parar e remover tudo, INCLUSIVE os dados
docker compose down -v

# Reiniciar apenas a aplicação
docker compose restart app

# Acessar o shell do container da aplicação
docker exec -it forum_app sh

# Acessar o psql do banco
docker exec -it forum_db psql -U forumuser -d forumdb
```

---

## Comandos do Docker Compose

### Subir o ambiente

```bash
docker compose up -d --build
```

### Verificar containers em execução

```bash
docker compose ps
docker ps
```

### Visualizar logs

```bash
docker compose logs -f          # todos
docker compose logs -f app      # apenas app
docker compose logs -f db       # apenas banco
```

### Verificar volumes

```bash
docker volume ls
docker volume inspect forum-online_forum_db_data
```

### Derrubar containers

```bash
docker compose down             # mantém volume
docker compose down -v          # remove volume também
```

---

## 🗃 Persistência de Dados

A persistência é garantida pelo volume Docker nomeado `forum_db_data`, declarado no `docker-compose.yml`:

```yaml
volumes:
  - forum_db_data:/var/lib/postgresql/data
```

**Teste de persistência:**

1. Cadastre um usuário e crie um tópico na aplicação.
2. Pare os containers: `docker compose down`
3. Suba novamente: `docker compose up -d`
4. Acesse a aplicação: os dados estarão lá. ✅

Para remover os dados, é necessário derrubar com a flag `-v`:

```bash
docker compose down -v
```

---

## 🐋 Imagem no DockerHub

A imagem da aplicação está publicada em:

```
docker pull rafaelzink/forum-online-app:latest
```

### Como publicar a imagem (passo a passo)

```bash
# 1. Fazer login no DockerHub
docker login

# 2. Buildar a imagem com tag do seu usuário
docker build -t rafaelzink/forum-online-app:latest .

# 3. Publicar
docker push rafaelzink/forum-online-app:latest
```

Para usar a imagem do DockerHub no `docker-compose.yml`, substitua o bloco `build` do serviço `app` por:

```yaml
app:
  image: rafaelzink/forum-online-app:latest
```

---

## 📁 Estrutura do Projeto

```
forum-online/
├── app/
│   ├── app.py                  # Aplicação Flask principal
│   ├── requirements.txt        # Dependências Python
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── usuarios.html
│   │   ├── novo_usuario.html
│   │   ├── novo_topico.html
│   │   └── topico.html
│   └── static/
│       └── css/
│           └── style.css
├── evidencias/                 # Prints da execução
├── Dockerfile                  # Imagem da aplicação
├── docker-compose.yml          # Orquestração dos containers
├── .env                        # Variáveis de ambiente
├── .dockerignore
├── .gitignore
└── README.md
```

---

## Checklist do Trabalho

- [x] 1 container da aplicação (Flask)
- [x] 1 container do banco de dados (PostgreSQL)
- [x] Comunicação entre containers via rede Docker
- [x] Persistência de dados utilizando volume nomeado
- [x] Orquestração com Docker Compose
- [x] Publicação da imagem no DockerHub
- [x] Interface funcional
- [x] Conexão da aplicação ao banco
- [x] Cadastro e consulta de informações (CRUD em usuários, tópicos e respostas)
- [x] Aplicação relacionada ao tema **Infraestrutura para um Fórum Online**

---

## Autor

Trabalho desenvolvido por Rafael Zink para a disciplina de **Cloud Computing**, ministrada pelo **Prof. Esp. Ademar Perfoll Junior** no curso de **Sistemas de Informação** da **UNIDAVI**.
