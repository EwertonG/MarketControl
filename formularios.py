from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators, SelectField, IntegerField

class FormularioProduto(FlaskForm):
    nome_produto = StringField('Nome do Produto', [validators.DataRequired(), validators.Length(min=1, max=100)])
    codigo = StringField('Código', [validators.DataRequired(), validators.Length(min=1, max=50)])
    preco = StringField('Preço', [validators.DataRequired(), validators.Length(min=1, max=20)])
    quantidade = StringField('Quantidade', [validators.DataRequired(), validators.Length(min=1, max=50)])
    data_validade = StringField('Data de Validade', [validators.DataRequired(), validators.Length(min=1, max=20)])
    fornecedor_id = SelectField('Fornecedor', coerce=int, validators=[validators.DataRequired()])
    categoria = StringField('Categoria', [validators.DataRequired(), validators.Length(min=1, max=50)])
    salvar = SubmitField('Salvar')

class FormularioUsuario(FlaskForm):
    nickname = StringField('Usuário',[validators.DataRequired(), validators.Length(min=1, max=50)] )
    senha = PasswordField ('Senha', [validators.DataRequired(), validators.Length(min=1, max=50)])
    login = SubmitField('Login')

class FormularioCadastro(FlaskForm):
    nome = StringField('Nome Completo', [validators.DataRequired(), validators.Length(min=1, max=100)])
    nickname = StringField('Usuário (Nickname)', [validators.DataRequired(), validators.Length(min=1, max=50)])
    senha = PasswordField('Senha', [validators.DataRequired(), validators.Length(min=1, max=50)])
    cadastrar = SubmitField('Finalizar Cadastro')

class FormularioFornecedor(FlaskForm):
    nome_fornecedor = StringField('Nome do Fornecedor', [validators.DataRequired(), validators.Length(min=1, max=255)])
    telefone = StringField('Telefone', [validators.Length(min=0, max=50)])
    email = StringField('E-mail', [validators.Length(min=0, max=100)])
    salvar = SubmitField('Salvar Fornecedor')