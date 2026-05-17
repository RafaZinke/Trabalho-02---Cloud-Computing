# 📸 Guia de Evidências - Trabalho 02

Este arquivo lista **todos os prints obrigatórios** que devem ser capturados nesta pasta para a entrega do trabalho.

> ⚠ **Importante:** Todos os prints devem ser capturados da SUA máquina, com o terminal visível. Não use prints da internet, imagens genéricas ou imagens geradas por IA.

---

## 🔢 Ordem sugerida para captura

Execute os comandos abaixo na ordem e tire um print após cada etapa.

### 1️⃣ Desenvolvimento - Aplicação rodando localmente

Após subir os containers, abra `http://localhost:5000` no navegador e capture:

- `01_app_local_index.png` - Página inicial do fórum
- `02_app_local_usuarios.png` - Página de usuários (com pelo menos 1 cadastrado)
- `03_app_local_topico.png` - Visualização de um tópico com resposta

---

### 2️⃣ Docker - Build da imagem

```bash
docker build -t forum-online-app:latest .
```

📸 Capture: `04_docker_build.png` (terminal mostrando o build completo)

---

### 3️⃣ Docker - Listar imagens

```bash
docker images
```

📸 Capture: `05_docker_images.png` (mostrando a imagem `forum-online-app` e `postgres`)

---

### 4️⃣ Docker Compose - Subir os containers

```bash
docker compose up -d --build
```

📸 Capture: `06_docker_compose_up.png` (saída do comando)

Em seguida:

```bash
docker compose logs --tail=20
```

📸 Capture: `07_docker_compose_logs.png` (mostrando app conectado ao banco)

---

### 5️⃣ Docker - Listar containers em execução

```bash
docker ps
```

📸 Capture: `08_docker_ps.png` (mostrando `forum_app` e `forum_db` rodando)

---

### 6️⃣ Comunicação entre containers

Acesse o container do app e ping no container do banco:

```bash
docker exec -it forum_app sh -c "python -c 'import psycopg2; c=psycopg2.connect(host=\"db\", dbname=\"forumdb\", user=\"forumuser\", password=\"forumpass\"); print(\"Conectado:\", c)'"
```

📸 Capture: `09_comunicacao_containers.png` (saída mostrando conexão bem-sucedida)

Ou, mais simples, acesse o psql diretamente pelo container do app via rede interna:

```bash
docker exec -it forum_db psql -U forumuser -d forumdb -c "SELECT version();"
```

📸 Capture: `10_psql_version.png`

---

### 7️⃣ Cadastro e consulta funcionando

Na interface web (`http://localhost:5000`):

1. Cadastre um usuário em `/usuarios/novo`
2. Crie um tópico em `/topicos/novo`
3. Adicione uma resposta no tópico

📸 Capture:
- `11_cadastro_usuario.png` - Formulário de cadastro preenchido
- `12_cadastro_topico.png` - Formulário de tópico preenchido
- `13_consulta_topicos.png` - Lista de tópicos na home
- `14_topico_com_resposta.png` - Tópico mostrando a resposta cadastrada

Confira os dados diretamente no banco:

```bash
docker exec -it forum_db psql -U forumuser -d forumdb -c "SELECT * FROM usuarios;"
docker exec -it forum_db psql -U forumuser -d forumdb -c "SELECT * FROM topicos;"
docker exec -it forum_db psql -U forumuser -d forumdb -c "SELECT * FROM respostas;"
```

📸 Capture: `15_select_no_banco.png` (mostrando os dados no PostgreSQL)

---

### 8️⃣ Volumes - Listar volume

```bash
docker volume ls
```

📸 Capture: `16_docker_volume_ls.png` (mostrando `forum-online_forum_db_data`)

```bash
docker volume inspect forum-online_forum_db_data
```

📸 Capture: `17_docker_volume_inspect.png`

---

### 9️⃣ Persistência dos dados

Teste a persistência:

```bash
# 1) Confirme que tem dados
docker exec -it forum_db psql -U forumuser -d forumdb -c "SELECT COUNT(*) FROM usuarios;"

# 2) Pare os containers
docker compose down

# 3) Suba novamente
docker compose up -d

# 4) Verifique que os dados continuam lá
docker exec -it forum_db psql -U forumuser -d forumdb -c "SELECT COUNT(*) FROM usuarios;"
```

📸 Capture: `18_persistencia_dados.png` (mostrando o COUNT antes e depois do down/up — pode ser uma sequência em um único terminal)

---

### 🔟 DockerHub - Login

```bash
docker login
```

📸 Capture: `19_docker_login.png` (mostrando "Login Succeeded")

---

### 1️⃣1️⃣ DockerHub - Tag + Push

```bash
docker tag forum-online-app:latest SEU_USUARIO/forum-online-app:latest
docker push SEU_USUARIO/forum-online-app:latest
```

📸 Capture: `20_docker_push.png` (mostrando o push completo)

---

### 1️⃣2️⃣ DockerHub - Página pública

Acesse `https://hub.docker.com/r/SEU_USUARIO/forum-online-app`

📸 Capture: `21_dockerhub_publico.png` (página da imagem no DockerHub)

---

## ✅ Resumo dos prints obrigatórios

| # | Arquivo | Item exigido |
|---|---------|--------------|
| 1-3 | app_local_*.png | Aplicação funcionando localmente |
| 4 | docker_build.png | `docker build` |
| 5 | docker_images.png | `docker images` |
| 6-7 | docker_compose_*.png | `docker compose up` |
| 8 | docker_ps.png | `docker ps` |
| 9-10 | comunicacao_*.png | Aplicação conectando ao banco |
| 11-15 | cadastro_/consulta_*.png | Cadastro e consulta funcionando |
| 16-17 | docker_volume_*.png | `docker volume ls` |
| 18 | persistencia_dados.png | Persistência |
| 19 | docker_login.png | `docker login` |
| 20 | docker_push.png | `docker push` |
| 21 | dockerhub_publico.png | Página pública da imagem |

---

> Após capturar todos os prints, faça commit desta pasta no GitHub junto com o restante do projeto.
