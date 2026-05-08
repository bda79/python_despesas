# Control Despesas 💰

Uma aplicação web para gerenciar e controlar despesas pessoais de forma simples e intuitiva.

## 📋 Funcionalidades

- ✅ **Autenticação de Utilizadores** - Login e logout seguro
- ✅ **Registo de Despesas** - Adicione novas despesas com categoria, valor, data e descrição
- ✅ **Histórico de Despesas** - Visualize todas as suas despesas em uma tabela organizada
- ✅ **Editar Despesas** - Modifique despesas registadas anteriormente
- ✅ **Apagar Despesas** - Remova despesas com confirmação em modal
- ✅ **Categorização** - Organize despesas por categoria
- ✅ **Filtro e Ordenação** - Despesas ordenadas por data (mais recentes primeiro)
- ✅ **Notificações** - Mensagens de sucesso e erro com auto-dismiss
- ✅ **Interface Responsiva** - Compatível com desktop e dispositivos móveis

## 🛠️ Tecnologias

- **Backend:** Django 6.0.3 (Python Web Framework)
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3, JavaScript
- **Autenticação:** Django Built-in Authentication
- **Ícones:** Font Awesome
- **Tipografia:** Google Fonts (Nunito)
- **CSS Reset:** Modern Normalize

## 📦 Requisitos

- Python 3.8+
- Django 6.0.3
- pip (Python Package Manager)

## 🚀 Instalação e Setup

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/control-despesas.git
cd control-despesas
```

### 2. Crie um ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute as migrações

```bash
cd despesas
python manage.py migrate
```

### 5. Crie um superutilizador (Admin)

```bash
python manage.py createsuperuser
```

### 6. Inicie o servidor de desenvolvimento

```bash
python manage.py runserver
```

A aplicação estará disponível em `http://127.0.0.1:8000/`

## 📁 Estrutura do Projeto

```
control-despesas/
├── README.md                          # Este ficheiro
├── despesas/                          # Pasta do projeto Django
│   ├── manage.py                      # Script de gestão do Django
│   ├── db.sqlite3                     # Base de dados SQLite
│   ├── despesas/                      # Configurações do projeto
│   │   ├── settings.py                # Configurações do Django
│   │   ├── urls.py                    # URLs principais
│   │   ├── wsgi.py                    # Configuração WSGI
│   │   └── asgi.py                    # Configuração ASGI
│   ├── expenses/                      # Aplicação de despesas
│   │   ├── models.py                  # Modelos (Despesa, Categoria)
│   │   ├── views.py                   # Vistas (lógica da aplicação)
│   │   ├── urls.py                    # URLs das despesas
│   │   ├── forms.py                   # Formulários
│   │   ├── admin.py                   # Configuração admin
│   │   ├── migrations/                # Migrações do banco de dados
│   │   ├── templates/                 # Templates HTML
│   │   │   ├── base.html              # Template base
│   │   │   ├── lista.html             # Listagem de despesas
│   │   │   ├── nova_despesa.html      # Formulário de nova despesa
│   │   │   ├── login.html             # Página de login
│   │   │   └── confirmar_apagar.html  # Confirmação de apagar
│   │   └── templatetags/              # Custom template filters
│   │       └── custom_filters.py      # Filtros personalizados
│   └── venv/                    # Ambiente virtual
```

## 👤 Utilização

### Fazer Login

1. Aceda a `http://127.0.0.1:8000/login/`
2. Insira o seu nome de utilizador e senha
3. Clique em "Entrar"

### Adicionar uma Despesa

1. Clique em "Adicionar Despesa" na navegação
2. Preencha os detalhes:
   - **Categoria:** Selecione uma categoria existente
   - **Valor:** Insira o valor em euros
   - **Data:** Selecione a data da despesa
   - **Descrição:** Adicione uma nota (opcional)
3. Clique em "Guardar Despesa"

### Visualizar Histórico

1. Clique em "Lista de Despesas" na navegação
2. Visualize todas as suas despesas ordenadas por data

### Editar uma Despesa

1. Na tabela de despesas, clique no botão "Editar"
2. Modifique os detalhes desejados
3. Clique em "Guardar Alterações"

### Apagar uma Despesa

1. Na tabela de despesas, clique no botão "Apagar"
2. Confirme a exclusão na modal que aparece
3. A despesa será removida imediatamente

## 🎨 Características de UI/UX

- **Navegação Ativa:** Links de navegação destacam-se quando estão ativos
- **Modal de Confirmação:** Confirmação elegante antes de apagar despesas
- **Mensagens Auto-Dismiss:** Mensagens de sucesso/erro desaparecem após 10 segundos
- **Design Responsivo:** Interface adapta-se a todos os tamanhos de ecrã
- **Tabela Scrollável:** Fácil visualização de muitas despesas
- **Ícones Font Awesome:** Interface visual intuitiva

## 🔒 Segurança

- ✅ Autenticação de utilizador obrigatória
- ✅ Proteção CSRF em formulários
- ✅ Cada utilizador só vê as suas despesas
- ✅ Validação de dados no servidor
- ✅ Senha armazenada de forma segura

## 📝 Notas de Desenvolvimento

- O projeto usa Django ORM para interação com a base de dados
- As despesas são filtradas por utilizador autenticado
- Categorias são geridas através do admin do Django
- Filtros customizados formatam valores monetários em euros

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se livre para:

- Relatar bugs
- Sugerir novas funcionalidades
- Enviar pull requests com melhorias

## 📄 Licença

Este projeto é licenciado sob a licença MIT.

## 👨‍💻 Autor

Desenvolvido por Bruno Aleluia

---

**Dúvidas ou problemas?** Abra uma issue no repositório do GitHub!
