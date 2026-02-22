import psycopg2
from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_wtf.csrf import CSRFProtect
from markupsafe import Markup

from formularios import FormularioProduto, FormularioUsuario, FormularioCadastro, FormularioFornecedor

app = Flask(__name__)
app.secret_key = 'ewerton'

csrf = CSRFProtect(app)

class Produto:
    def __init__(self, id, nome_produto, codigo, preco, quantidade, data_validade, fornecedor_id, usuario_criador=None, categoria='Geral', nome_fornecedor=None):
        self.id = id
        self.nome_produto = nome_produto
        self.codigo = codigo
        self.preco = preco
        self.quantidade = quantidade
        self.data_validade = data_validade
        self.fornecedor_id = fornecedor_id
        self.usuario_criador = usuario_criador
        self.categoria = categoria
        self.nome_fornecedor = nome_fornecedor

class Usuario:
    def __init__(self, nome, nickname, senha):
        self.nome = nome
        self.nickname = nickname
        self.senha = senha

class Fornecedor:
    def __init__(self, id, nome_fornecedor, telefone, email):
        self.id = id
        self.nome_fornecedor = nome_fornecedor
        self.telefone = telefone
        self.email = email

def conecta_bd():
    return psycopg2.connect(
        host="localhost",
        database="loja",
        user="postgres",
        password="29033"
    )

def buscar_produtos():
    conn = conecta_bd()
    cur = conn.cursor()
    cur.execute('''
        SELECT p.id, p.nome_produto, p.codigo, p.preco, p.quantidade, 
               p.data_validade, p.fornecedor_id, p.usuario_criador, p.categoria, f.nome_fornecedor 
        FROM produtos p
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        ORDER BY p.id DESC
    ''')
    produtos = cur.fetchall()
    conn.close()
    return [Produto(*produto) for produto in produtos]

def buscar_fornecedores():
    conn = conecta_bd()
    cur = conn.cursor()
    cur.execute('SELECT id, nome_fornecedor, telefone, email FROM fornecedores ORDER BY nome_fornecedor')
    fornecedores = cur.fetchall()
    conn.close()
    # Retorna lista de objetos Fornecedor
    return [Fornecedor(*f) for f in fornecedores]

def adicionar_produto(produto):
    conn = conecta_bd()
    cur = conn.cursor()
    cur.execute('INSERT INTO produtos (nome_produto, codigo, preco, quantidade, data_validade, fornecedor_id, usuario_criador, categoria) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                (produto.nome_produto, produto.codigo, produto.preco, produto.quantidade, produto.data_validade, produto.fornecedor_id, produto.usuario_criador, produto.categoria))
    conn.commit()
    conn.close()

def buscar_produtos_por_usuario(nickname):
    conn = conecta_bd()
    cur = conn.cursor()
    cur.execute('''
        SELECT p.id, p.nome_produto, p.codigo, p.preco, p.quantidade, 
               p.data_validade, p.fornecedor_id, p.usuario_criador, p.categoria, f.nome_fornecedor 
        FROM produtos p
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        WHERE p.usuario_criador = %s 
        ORDER BY p.id DESC
    ''', (nickname,))
    produtos = cur.fetchall()
    conn.close()
    return [Produto(*produto) for produto in produtos]

def buscar_usuarios():
    conn = conecta_bd()
    cur = conn.cursor()
    cur.execute('SELECT nome, nickname, senha FROM usuarios')
    usuarios = cur.fetchall()
    conn.close()
    return {usuario[1]: Usuario(*usuario) for usuario in usuarios}

@app.route('/')
def index():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login'))

    produtos = buscar_produtos()
    return render_template('lista.html', titulo='MarketControl', produtos=produtos)

@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('novo')))
    
    form = FormularioProduto()
    fornecedores = buscar_fornecedores()
    form.fornecedor_id.choices = [(f.id, f.nome_fornecedor) for f in fornecedores]
    
    return render_template('novo.html', titulo='Cadastro de Produtos', form=form)

@app.route('/criar', methods=['POST'])
def criar():
    form = FormularioProduto(request.form)
    fornecedores = buscar_fornecedores()
    form.fornecedor_id.choices = [(f.id, f.nome_fornecedor) for f in fornecedores]

    if not form.validate_on_submit():
        flash('Erro ao preencher o formulário. Verifique os dados.', 'danger')
        return redirect(url_for('novo'))

    nome_produto = form.nome_produto.data
    codigo = form.codigo.data
    preco = form.preco.data
    quantidade = form.quantidade.data
    data_validade = form.data_validade.data
    fornecedor_id = form.fornecedor_id.data
    categoria = form.categoria.data
    usuario_logado = session.get('usuario_logado')

    conn = conecta_bd()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM produtos WHERE nome_produto = %s', (nome_produto,))
    existe_produto = cur.fetchone()[0] > 0

    if existe_produto:
        flash(f'Produto com o nome "{nome_produto}" já existe!', 'danger')
        conn.close()
        return redirect(url_for('novo'))

    novo_produto = Produto(None, nome_produto, codigo, preco, quantidade, data_validade, fornecedor_id, usuario_logado, categoria)
    adicionar_produto(novo_produto)
    conn.close()

    flash('Produto adicionado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('editar', id=id)))

    form = FormularioProduto()
    fornecedores = buscar_fornecedores()
    form.fornecedor_id.choices = [(f.id, f.nome_fornecedor) for f in fornecedores]

    if request.method == 'POST':
        if form.validate_on_submit():
            nome_produto = form.nome_produto.data
            codigo = form.codigo.data
            preco = form.preco.data
            quantidade = form.quantidade.data
            data_validade = form.data_validade.data
            fornecedor_id = form.fornecedor_id.data
            categoria = form.categoria.data

            conn = conecta_bd()
            cur = conn.cursor()
            cur.execute(
                'UPDATE produtos SET nome_produto = %s, codigo = %s, preco = %s, quantidade = %s, data_validade = %s, fornecedor_id = %s, categoria = %s WHERE id = %s',
                (nome_produto, codigo, preco, quantidade, data_validade, fornecedor_id, categoria, id)
            )
            conn.commit()
            conn.close()

            flash('Produto atualizado com sucesso!')
            return redirect(url_for('index'))
    else:
        conn = conecta_bd()
        cur = conn.cursor()
        cur.execute('SELECT id, nome_produto, codigo, preco, quantidade, data_validade, fornecedor_id, categoria FROM produtos WHERE id = %s', (id,))
        produto = cur.fetchone()
        conn.close()

        if produto:
            form.nome_produto.data = produto[1]
            form.codigo.data = produto[2]
            form.preco.data = produto[3]
            form.quantidade.data = produto[4]
            form.data_validade.data = produto[5]
            form.fornecedor_id.data = produto[6]
            # Atribuição segura para categoria
            form.categoria.data = produto[7] if len(produto) > 7 else 'Geral'
        else:
            flash('Produto não encontrado.')
            return redirect(url_for('index'))
            
    return render_template('editar.html', titulo='Edição de Produto', id=id, form=form)

@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login'))

    conn = conecta_bd()
    cur = conn.cursor()
    cur.execute('DELETE FROM produtos WHERE id = %s', (id,))
    conn.commit()
    conn.close()

    flash('Produto removido com sucesso!')
    return redirect(url_for('index'))

@app.route('/novo_fornecedor')
def novo_fornecedor():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('novo_fornecedor')))

    form = FormularioFornecedor()
    return render_template('novo_fornecedor.html', titulo='Cadastro de Fornecedor', form=form)

@app.route('/criar_fornecedor', methods=['POST'])
def criar_fornecedor():
    form = FormularioFornecedor(request.form)

    if not form.validate_on_submit():
        return redirect(url_for('novo_fornecedor'))

    nome_fornecedor = form.nome_fornecedor.data
    telefone = form.telefone.data
    email = form.email.data

    conn = conecta_bd()
    cur = conn.cursor()
    cur.execute('INSERT INTO fornecedores (nome_fornecedor, telefone, email) VALUES (%s, %s, %s)', 
                (nome_fornecedor, telefone, email))
    conn.commit()
    conn.close()

    flash('Fornecedor adicionado com sucesso!', 'success')
    return redirect(url_for('fornecedores'))

@app.route('/meus_produtos')
def meus_produtos():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('meus_produtos')))
    
    usuario_atual = session['usuario_logado']
    produtos = buscar_produtos_por_usuario(usuario_atual)
    return render_template('meus_produtos.html', titulo='Meus Produtos', produtos=produtos)

@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    form = FormularioCadastro(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        nome = form.nome.data
        nickname = form.nickname.data
        senha = form.senha.data

        conn = conecta_bd()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM usuarios WHERE nickname = %s', (nickname,))
        existe_usuario = cur.fetchone()[0] > 0

        if existe_usuario:
            flash(f'O usuário "{nickname}" já está em uso. Por favor, escolha outro.')
            conn.close()
            return redirect(url_for('cadastrar'))

        cur.execute('INSERT INTO usuarios (nome, nickname, senha) VALUES (%s, %s, %s)', (nome, nickname, senha))
        conn.commit()
        conn.close()

        flash('Cadastro realizado com sucesso! Agora você já pode fazer seu login.', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html', titulo='Cadastro de Usuário', form=form)

@app.route('/fornecedores')
def fornecedores():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('fornecedores')))
    lista = buscar_fornecedores()
    return render_template('fornecedores.html', titulo='Fornecedores', fornecedores=lista)

@app.route('/editar_fornecedor/<int:id>', methods=['GET', 'POST'])
def editar_fornecedor(id):
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login'))

    form = FormularioFornecedor()

    if request.method == 'POST' and form.validate_on_submit():
        nome = form.nome_fornecedor.data
        telefone = form.telefone.data
        email = form.email.data

        conn = conecta_bd()
        cur = conn.cursor()
        cur.execute('UPDATE fornecedores SET nome_fornecedor = %s, telefone = %s, email = %s WHERE id = %s', (nome, telefone, email, id))
        conn.commit()
        conn.close()

        flash('Fornecedor atualizado com sucesso!', 'success')
        return redirect(url_for('fornecedores'))
    else:
        conn = conecta_bd()
        cur = conn.cursor()
        cur.execute('SELECT id, nome_fornecedor, telefone, email FROM fornecedores WHERE id = %s', (id,))
        forn = cur.fetchone()
        conn.close()

        if forn:
            form.nome_fornecedor.data = forn[1]
            form.telefone.data = forn[2]
            form.email.data = forn[3]

    return render_template('editar_fornecedor.html', titulo='Editar Fornecedor', id=id, form=form)

@app.route('/deletar_fornecedor/<int:id>', methods=['POST'])
def deletar_fornecedor(id):
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login'))

    try:
        conn = conecta_bd()
        cur = conn.cursor()
        cur.execute('DELETE FROM fornecedores WHERE id = %s', (id,))
        conn.commit()
        conn.close()
        flash('Fornecedor removido com sucesso!', 'success')
    except Exception as e:
        flash('Não é possível excluir este fornecedor pois existem produtos vinculados a ele.', 'danger')
        
    return redirect(url_for('fornecedores'))

@app.route('/login')
def login():
    proxima = request.args.get('proxima', url_for('index'))
    form = FormularioUsuario()
    return render_template('login.html', proxima=proxima, form=form)

@app.route('/autenticar', methods=['POST'])
def autenticar():
    form = FormularioUsuario(request.form)

    if form.validate_on_submit():
        usuarios = buscar_usuarios()
        username = form.nickname.data

        if username in usuarios:
            usuario = usuarios[username]
            if form.senha.data == usuario.senha:
                session['usuario_logado'] = usuario.nickname
                flash(f'{usuario.nickname} logado com sucesso!')
                proxima_pagina = request.form.get('proxima', url_for('index'))
                return redirect(proxima_pagina)
        else:
            flash('Usuário não encontrado.')
    else:
        flash('Formulário inválido.')

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)