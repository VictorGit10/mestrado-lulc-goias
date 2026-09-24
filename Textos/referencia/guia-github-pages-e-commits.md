# Guia Rápido: Commits + GitHub Pages

Guia para publicar páginas estáticas no GitHub Pages e manter um histórico de commits limpo.

---

## 1. Pré-requisitos

- Conta no GitHub (`github.com/signup`)
- Git instalado (`git --version`)
- Repositório criado no GitHub

---

## 2. Configurar acesso ao GitHub pela primeira vez

### 2.1. Configurar identidade do Git

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"
```

### 2.2. Autenticação: Token de Acesso Pessoal (PAT)

O GitHub não aceita mais senha em `git push`. Use um token.

**Gerar token:**
1. Acesse `github.com` → clique na sua foto (canto superior direito) → **Settings**
2. No menu lateral inferior, clique em **Developer settings**
3. **Personal access tokens** → **Tokens (classic)** → **Generate new token**
4. Marque o escopo **repo** (acesso completo aos repositórios)
5. Gere e copie o token (ele aparece apenas uma vez)

**Usar o token:**
```bash
# Ao clonar ou ao fazer push, use o token como senha
git clone https://github.com/USUARIO/REPO.git
# usuário: seu usuário do GitHub
# senha: cole o token
```

**Salvar token para não digitar toda vez (cache):**
```bash
git config --global credential.helper cache        # Linux/Mac
git config --global credential.helper manager-core   # Windows (Git Credential Manager)
```

### 2.3. Autenticação: SSH (alternativa ao token)

Mais seguro e não precisa digitar senha/token após configurado.

**Gerar chave:**
```bash
ssh-keygen -t ed25519 -C "seu.email@exemplo.com"
# pressione Enter para aceitar o caminho padrão
# defina uma senha (passphrase) ou deixe em branco
```

**Adicionar ao GitHub:**
1. Copie a chave pública:
   ```bash
   cat ~/.ssh/id_ed25519.pub   # Linux/Mac
   type %USERPROFILE%\.ssh\id_ed25519.pub   # Windows
   ```
2. No GitHub: **Settings** → **SSH and GPG keys** → **New SSH key**
3. Cole o conteúdo e salve.

**Usar SSH:**
```bash
# Clone via SSH (note o git@github.com:)
git clone git@github.com:USUARIO/REPO.git

# Ou altere um remote existente de HTTPS para SSH
git remote set-url origin git@github.com:USUARIO/REPO.git
```

### 2.4. Verificar se funcionou

```bash
git remote -v
```
Deve aparecer a URL do seu repositório.

---

## 3. Estrutura mínima para GitHub Pages

```
repo/
├── index.html          # obrigatório: página inicial
├── css/                # estilos
├── js/                 # scripts
├── assets/             # imagens, fontes, etc.
└── README.md           # opcional mas recomendado
```

> **Importante:** o `index.html` deve estar na raiz ou na pasta configurada nas settings do Pages.

---

## 4. Criar repositório e vincular projeto existente

Se você já tem uma pasta local com arquivos:

```bash
# Dentro da pasta do projeto
git init
git add .
git commit -m "feat: commit inicial"
git branch -M main          # ou master
git remote add origin https://github.com/USUARIO/REPO.git
git push -u origin main
```

---

## 5. Configurar GitHub Pages no repositório

1. Acesse o repositório no GitHub
2. Vá em **Settings** → **Pages** (ou *Configurações* → *Páginas*)
3. Em **Source** (*Fonte*), selecione:
   - **Deploy from a branch**
   - Branch: `master` ou `main`
   - Pasta: `/ (root)` ou `/docs` (se preferir)
4. Salve. O link será algo como: `https://<usuario>.github.io/<repo>/`

---

## 6. Padrão de commits (conventional commits em pt-BR)

Prefixo obrigatório + descrição no imperativo/presente:

| Prefixo | Uso |
|---------|-----|
| `feat:` | nova funcionalidade |
| `fix:` | correção de bug |
| `ajuste:` | ajuste visual, texto, estilo |
| `docs:` | documentação (README, comentários) |
| `refactor:` | refatoração sem mudar comportamento |
| `chore:` | tarefas de build, dependências |
| `remove:` | remoção de arquivo ou funcionalidade |

### Exemplos

```bash
git commit -m "feat: adiciona filtro de anos no dashboard"
git commit -m "fix: corrige quebra de layout no mobile"
git commit -m "ajuste: atualiza cores e tipografia do slide 3"
git commit -m "docs: adiciona seção de metodologia no README"
```

---

## 7. Fluxo de publicação (passo a passo)

### Verificar o estado atual

```bash
git status
git diff          # ver alterações antes de commitar
git log --oneline -5   # ver últimos commits
```

### Preparar e commitar

```bash
# Adicionar arquivos específicos (evite git add . se houver arquivos indesejados)
git add index.html css/ js/

# Criar o commit
git commit -m "feat: adiciona visualização interativa de mapa"
```

### Enviar para o GitHub

```bash
# Primeiro push (se a branch ainda não existe no remote)
git push -u origin main

# Push subsequentes
git push origin main
```

### Aguardar o deploy

- GitHub Pages pode levar de **30 segundos a 2 minutos** para refletir as mudanças.
- Para verificar o status do deploy: abra o link do Pages em uma aba anônima para evitar cache do navegador.

---

## 8. Atualizar GitHub Pages após mudanças

```bash
# 1. Verifique o que mudou
git status

# 2. Adicione os arquivos alterados
git add <arquivos>

# 3. Commit
git commit -m "fix: corrige texto do título principal"

# 4. Push
git push origin main

# 5. Aguarde e recarregue a página publicada
```

---

## 9. `.gitignore` essencial

Crie um arquivo `.gitignore` na raiz para evitar commitar arquivos desnecessários:

```gitignore
# Sistema operacional
.DS_Store
Thumbs.db

# Editores
.vscode/
.idea/
*.swp

# Dependências (se houver)
node_modules/

# Arquivos temporários
*.tmp
*.log
```

---

## 10. Dicas rápidas

| Situação | Comando / Ação |
|----------|----------------|
| Ver link do remote | `git remote -v` |
| Trocar de branch | `git checkout -b nova-branch` |
| Desfazer alterações não commitadas | `git restore <arquivo>` |
| Ver histórico detalhado | `git log --oneline --graph` |
| Forçar refresh no navegador | `Ctrl + F5` ou abrir em aba anônima |
| Mensagem de commit errada | `git commit --amend` (apenas antes do push) |
| Ver quem alterou cada linha | `git blame <arquivo>` |
| Renomear arquivo | `git mv <antigo> <novo>` |
| Ver branches existentes | `git branch -a` |

---

## 11. Troubleshooting comum

| Problema | Solução |
|----------|---------|
| Erro de autenticação ao push | Verifique se está usando token (não senha do GitHub) ou se a chave SSH está adicionada ao agente (`ssh-add ~/.ssh/id_ed25519`) |
| Página não atualiza | Aguarde 1-2 min; limpe cache (`Ctrl+F5`); verifique se o arquivo está na branch correta |
| Assets (imagens/JS) não carregam | Verifique caminhos relativos (ex: `css/style.css` em vez de `/css/style.css` se for subpasta) |
| 404 no link do Pages | Confirme que `index.html` existe na raiz; verifique se Pages está ativado nas Settings |
| Push rejeitado | Faça `git pull origin main` antes do push para integrar mudanças remotas |
| Erro `fatal: not a git repository` | Você está fora da pasta do projeto. Use `cd <pasta>` |

---

## Template de commit (copie e cole)

```bash
git add <arquivos>
git commit -m "<prefixo>: <descrição curta e direta no presente>"
git push origin main
```

---

*Gerado para projetos de visualização estática com GitHub Pages.*
