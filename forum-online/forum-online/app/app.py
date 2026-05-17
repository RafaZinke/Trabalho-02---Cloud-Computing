"""
Forum Online - Aplicacao Flask
Trabalho 02 - Cloud Computing - UNIDAVI
Tema: Infraestrutura para um Forum Online
"""
import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "forum-online-secret-key")

# Configuracoes do banco vindas das variaveis de ambiente (docker-compose)
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "db"),
    "port": os.environ.get("DB_PORT", "5432"),
    "database": os.environ.get("DB_NAME", "forumdb"),
    "user": os.environ.get("DB_USER", "forumuser"),
    "password": os.environ.get("DB_PASSWORD", "forumpass"),
}


def get_connection():
    """Cria uma nova conexao com o PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """
    Inicializa as tabelas do banco.
    Faz retry porque o container do banco pode demorar a aceitar conexoes.
    """
    tentativas = 15
    for tentativa in range(1, tentativas + 1):
        try:
            conn = get_connection()
            cur = conn.cursor()

            # Tabela de usuarios do forum
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    email VARCHAR(150) UNIQUE NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Tabela de topicos do forum
            cur.execute("""
                CREATE TABLE IF NOT EXISTS topicos (
                    id SERIAL PRIMARY KEY,
                    titulo VARCHAR(200) NOT NULL,
                    conteudo TEXT NOT NULL,
                    categoria VARCHAR(50) NOT NULL,
                    autor_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Tabela de respostas dos topicos
            cur.execute("""
                CREATE TABLE IF NOT EXISTS respostas (
                    id SERIAL PRIMARY KEY,
                    topico_id INTEGER REFERENCES topicos(id) ON DELETE CASCADE,
                    autor_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                    conteudo TEXT NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.commit()
            cur.close()
            conn.close()
            print(f"[OK] Banco inicializado na tentativa {tentativa}")
            return
        except Exception as e:
            print(f"[ERRO] Tentativa {tentativa}/{tentativas}: {e}")
            time.sleep(2)
    raise RuntimeError("Nao foi possivel conectar ao banco de dados.")


# -------------------------- ROTAS PRINCIPAIS --------------------------

@app.route("/")
def index():
    """Pagina inicial - lista topicos e estatisticas do forum."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT t.id, t.titulo, t.categoria, t.criado_em,
               u.nome AS autor,
               (SELECT COUNT(*) FROM respostas r WHERE r.topico_id = t.id) AS qtd_respostas
        FROM topicos t
        JOIN usuarios u ON u.id = t.autor_id
        ORDER BY t.criado_em DESC;
    """)
    topicos = cur.fetchall()

    cur.execute("SELECT COUNT(*) AS total FROM usuarios;")
    total_usuarios = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM topicos;")
    total_topicos = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM respostas;")
    total_respostas = cur.fetchone()["total"]

    cur.close()
    conn.close()

    return render_template(
        "index.html",
        topicos=topicos,
        total_usuarios=total_usuarios,
        total_topicos=total_topicos,
        total_respostas=total_respostas,
    )


# -------------------------- USUARIOS (CRUD) --------------------------

@app.route("/usuarios")
def listar_usuarios():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM usuarios ORDER BY criado_em DESC;")
    usuarios = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("usuarios.html", usuarios=usuarios)


@app.route("/usuarios/novo", methods=["GET", "POST"])
def novo_usuario():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()

        if not nome or not email:
            flash("Preencha todos os campos.", "erro")
            return redirect(url_for("novo_usuario"))

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO usuarios (nome, email) VALUES (%s, %s);",
                (nome, email),
            )
            conn.commit()
            cur.close()
            conn.close()
            flash(f"Usuario '{nome}' cadastrado com sucesso!", "sucesso")
            return redirect(url_for("listar_usuarios"))
        except psycopg2.errors.UniqueViolation:
            flash("Este e-mail ja esta cadastrado.", "erro")
            return redirect(url_for("novo_usuario"))
        except Exception as e:
            flash(f"Erro ao cadastrar usuario: {e}", "erro")
            return redirect(url_for("novo_usuario"))

    return render_template("novo_usuario.html")


@app.route("/usuarios/<int:usuario_id>/excluir", methods=["POST"])
def excluir_usuario(usuario_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = %s;", (usuario_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Usuario excluido com sucesso!", "sucesso")
    return redirect(url_for("listar_usuarios"))


# -------------------------- TOPICOS (CRUD) --------------------------

@app.route("/topicos/novo", methods=["GET", "POST"])
def novo_topico():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, nome FROM usuarios ORDER BY nome;")
    usuarios = cur.fetchall()
    cur.close()
    conn.close()

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        conteudo = request.form.get("conteudo", "").strip()
        categoria = request.form.get("categoria", "").strip()
        autor_id = request.form.get("autor_id")

        if not titulo or not conteudo or not categoria or not autor_id:
            flash("Preencha todos os campos.", "erro")
            return redirect(url_for("novo_topico"))

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO topicos (titulo, conteudo, categoria, autor_id)
               VALUES (%s, %s, %s, %s);""",
            (titulo, conteudo, categoria, autor_id),
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Topico criado com sucesso!", "sucesso")
        return redirect(url_for("index"))

    return render_template("novo_topico.html", usuarios=usuarios)


@app.route("/topicos/<int:topico_id>")
def ver_topico(topico_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT t.*, u.nome AS autor
        FROM topicos t
        JOIN usuarios u ON u.id = t.autor_id
        WHERE t.id = %s;
    """, (topico_id,))
    topico = cur.fetchone()

    if topico is None:
        cur.close()
        conn.close()
        flash("Topico nao encontrado.", "erro")
        return redirect(url_for("index"))

    cur.execute("""
        SELECT r.*, u.nome AS autor
        FROM respostas r
        JOIN usuarios u ON u.id = r.autor_id
        WHERE r.topico_id = %s
        ORDER BY r.criado_em ASC;
    """, (topico_id,))
    respostas = cur.fetchall()

    cur.execute("SELECT id, nome FROM usuarios ORDER BY nome;")
    usuarios = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "topico.html", topico=topico, respostas=respostas, usuarios=usuarios
    )


@app.route("/topicos/<int:topico_id>/responder", methods=["POST"])
def responder_topico(topico_id):
    conteudo = request.form.get("conteudo", "").strip()
    autor_id = request.form.get("autor_id")

    if not conteudo or not autor_id:
        flash("Preencha todos os campos da resposta.", "erro")
        return redirect(url_for("ver_topico", topico_id=topico_id))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO respostas (topico_id, autor_id, conteudo)
           VALUES (%s, %s, %s);""",
        (topico_id, autor_id, conteudo),
    )
    conn.commit()
    cur.close()
    conn.close()
    flash("Resposta enviada!", "sucesso")
    return redirect(url_for("ver_topico", topico_id=topico_id))


@app.route("/topicos/<int:topico_id>/excluir", methods=["POST"])
def excluir_topico(topico_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM topicos WHERE id = %s;", (topico_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Topico excluido.", "sucesso")
    return redirect(url_for("index"))


# -------------------------- HEALTHCHECK --------------------------

@app.route("/health")
def health():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return {"status": "ok", "db": "ok"}, 200
    except Exception as e:
        return {"status": "erro", "erro": str(e)}, 500


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
