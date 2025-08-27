# 🎓LIVIA🌼 - Sistema de Análise de Desempenho Acadêmico

**Levantamento de Informações Vinculadas à Infrequência e Avaliação**  
*E.E. Anna Passamonti Balardin*

Sistema web estático para análise de dados educacionais com funcionalidades de busca por aluno, monitoramento de notas e frequência, e geração de relatórios de risco.

## 🚀 Deploy Rápido

### Vercel (Recomendado)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/dansfisica85/Balardin)

1. **Fork este repositório**
2. **Conecte ao Vercel**:
   - Acesse [vercel.com](https://vercel.com)
   - Importe seu repositório
   - Deploy automático em segundos

3. **Acesse sua aplicação**: `https://seu-projeto.vercel.app`

### GitHub Pages (Alternativo)
1. Ative GitHub Pages nas configurações do repositório
2. Selecione a branch `main` como fonte
3. Acesse: `https://usuario.github.io/nome-do-repo`

## ✨ Funcionalidades

### 🔍 Busca Individual
- Seleção por turma e série/ano
- Busca específica por aluno
- Visualização detalhada de notas e frequência
- Alertas automáticos para:
  - **🔴 Risco de Evasão**: Frequência < 75%
  - **⚠️ Risco de Reprovação**: Médias < 5.0

### 📊 Relatórios Gerais
- **Relatório de Notas Baixas**: Estudantes com médias < 5.0 agrupados por série
- **Relatório de Frequência Baixa**: Estudantes com frequência < 75% agrupados por série
- **Relatório Combinado**: Análise integrada de ambos os riscos

### ⚡ Recursos Técnicos
- **100% Estático**: Sem necessidade de servidor backend
- **Dados Compilados**: JSON pré-processado para carregamento rápido
- **Interface Responsiva**: Funciona em desktop, tablet e mobile
- **Alertas Visuais**: Destaque automático para situações de risco

## 📁 Estrutura do Projeto

```
Balardin/
├── index.html              # Página principal
├── css/
│   └── style.css          # Estilos CSS
├── js/
│   └── script.js          # JavaScript principal
├── data/
│   └── alunos_compilado.json  # Dados dos alunos (compilados)
├── vercel.json            # Configuração do Vercel
├── *.pdf                  # Arquivos PDF originais
└── README.md              # Este arquivo
```

## 🎯 Como Usar

### 1. Busca Individual de Aluno
1. **Turma**: Selecione no primeiro dropdown (ex: 1A, 2B, 3C)
2. **Série**: Escolha a série/ano
3. **Aluno**: Selecione o estudante específico
4. **Buscar**: Clique no botão para visualizar dados completos

### 2. Relatórios por Risco
- **🟡 Notas Baixas**: Estudantes com risco de reprovação
- **🔴 Frequência Baixa**: Estudantes com risco de evasão  
- **🔵 Combinado**: Visualização integrada dos riscos

### 3. Resumo por Série
- Visão geral de todas as séries
- Contadores de alunos por situação
- Acesso rápido aos relatórios específicos

## 📋 Dados Suportados

### Formato dos Arquivos
- **PDFs Originais**: `1A.pdf`, `1B.pdf`, `2A.pdf`, etc.
- **Dados Compilados**: `data/alunos_compilado.json`

### Critérios de Risco
- **Risco de Reprovação**: Média semestral < 5.0
- **Risco de Evasão**: Frequência semestral < 75%

### Informações Extraídas
- Nome completo do aluno
- RA (Registro Acadêmico)
- Série e turma
- Notas por disciplina (1º e 2º bimestres)
- Médias semestrais calculadas
- Frequência por disciplina e geral

## 🛠️ Desenvolvimento Local

```bash
# Clone o repositório
git clone https://github.com/dansfisica85/Balardin.git
cd Balardin

# Sirva os arquivos estáticos
python -m http.server 8000
# ou
npx serve .

# Acesse no navegador
open http://localhost:8000
```

## ⚙️ Configuração Técnica

### Vercel
O arquivo `vercel.json` está configurado para:
- Servir arquivos estáticos
- Cache otimizado para performance
- Headers corretos para JSON
- Redirects para SPA behavior

### Performance
- **Dados pré-compilados**: JSON estático para carregamento rápido
- **CSS/JS minificados**: Código otimizado para produção
- **Cache headers**: Configuração para cache eficiente
- **Responsive design**: Interface adaptável

## 🔧 Personalização

### Modificar Critérios de Risco
No arquivo `js/script.js`, procure por:
```javascript
// Critério de nota baixa
if (media < 5.0) { ... }

// Critério de frequência baixa  
if (frequencia < 75) { ... }
```

### Atualizar Dados
1. Substitua os PDFs na pasta raiz
2. Execute `python build_data.py` (se disponível)
3. Faça commit do novo `data/alunos_compilado.json`
4. Deploy automático no Vercel

## 🎨 Interface

- **Design Moderno**: Interface limpa e intuitiva
- **Cores Temáticas**: Verde para aprovação, amarelo para atenção, vermelho para risco
- **Animações Sutis**: Feedback visual para ações do usuário
- **Acessibilidade**: Contrastes adequados e navegação por teclado

## 📱 Responsividade

- **Desktop**: Layout completo com todas as funcionalidades
- **Tablet**: Interface adaptada para toque
- **Mobile**: Design otimizado para telas pequenas

## 🐛 Solução de Problemas

### Dados não carregam
1. Verifique se `data/alunos_compilado.json` existe
2. Abra o console do navegador (F12) para ver erros
3. Verifique se está servindo via HTTP (não file://)

### Interface quebrada
1. Confirme que `css/style.css` e `js/script.js` estão acessíveis
2. Verifique se os paths estão corretos
3. Teste em modo incógnito para evitar cache

### Deploy no Vercel
1. Confirme que o repositório está público ou conectado
2. Verifique se `vercel.json` está na raiz
3. Confira os logs de build no dashboard do Vercel

## 📊 Tecnologias

- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Dados**: JSON estático pré-compilado
- **Deploy**: Vercel, GitHub Pages
- **Design**: CSS Grid, Flexbox, Responsive Design
- **Performance**: Service Workers ready, optimized assets

## 📄 Licença

Sistema desenvolvido para análise educacional. Livre para uso e modificação conforme necessidades específicas da instituição.

## 🆘 Suporte

Para dúvidas ou problemas:
1. 📖 Consulte este README
2. 🔍 Verifique o console do navegador (F12)
3. 🌐 Teste o deploy no Vercel
4. 📧 Abra uma issue no GitHub

---

**Desenvolvido com ❤️ para educação de qualidade**

## Instalação

### Pré-requisitos
- Python 3.7 ou superior
- Arquivos PDF com dados dos alunos

### Passos de Instalação

1. **Clone ou baixe os arquivos do projeto**
   ```bash
   # Os arquivos já estão na pasta atual
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verifique se os PDFs estão na pasta do projeto**
   - Os arquivos PDF devem estar na mesma pasta do `app.py`
   - Formato esperado: `1A.pdf`, `2B.pdf`, etc.

4. **Execute a aplicação**
   ```bash
   python app.py
   ```

5. **Acesse o sistema**
   - Abra o navegador em: `http://localhost:5000`

## Estrutura do Projeto

```
Balardin/
├── app.py                 # Aplicação Flask principal
├── pdf_processor.py       # Processamento dos PDFs
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── templates/
│   └── index.html        # Interface principal
├── static/
│   ├── style.css         # Estilos CSS
│   └── script.js         # JavaScript
└── *.pdf                 # Arquivos PDF dos alunos
```

## Como Usar

### 1. Busca Individual de Aluno
1. Selecione a **Série/Ano** no primeiro dropdown
2. Selecione o **Aluno** no segundo dropdown
3. Clique em **"Buscar Dados do Aluno"**
4. Visualize as notas, médias e alertas

### 2. Relatórios Gerais
- **Notas Baixas**: Clique no botão laranja para ver todos os estudantes com risco de reprovação
- **Frequência Baixa**: Clique no botão vermelho para ver todos os estudantes com risco de evasão

### 3. Reprocessamento
- Use o botão **"Reprocessar PDFs"** quando adicionar novos arquivos PDF

## Formato dos Dados

O sistema extrai automaticamente:
- **Nome do Aluno**
- **Série/Ano** (baseado no nome do arquivo)
- **Disciplinas e Notas** (1º e 2º bimestres)
- **Médias Semestrais** (calculadas automaticamente)
- **Frequência** (porcentagem de presença)

## Alertas do Sistema

### 🔴 Risco de Evasão (Frequência < 75%)
- Destaque visual com animação
- Classificação por nível de risco (Alto/Médio)
- Prioridade máxima de atenção

### ⚠️ Risco de Reprovação (Média < 5.0)
- Identificação por disciplina
- Detalhamento das notas bimestrais
- Visualização clara das matérias em risco

## Personalização

### Modificar Critérios de Alerta
No arquivo `app.py`, você pode alterar:
```python
# Linha ~67: Critério de nota baixa
if disciplina.get('media_semestral', 0) < 5:

# Linha ~79: Critério de frequência baixa  
if dados.get('frequencia_media', 100) < 75:
```

### Adaptar Processamento de PDFs
No arquivo `pdf_processor.py`, função `parse_student_data()`:
- Ajuste os padrões de regex para seu formato específico
- Modifique a lista de disciplinas padrão
- Customize a extração de dados conforme necessário

## Solução de Problemas

### PDFs não são processados
1. Verifique se os arquivos estão no formato PDF
2. Confirme que os arquivos estão na pasta correta
3. Use o botão "Reprocessar PDFs"

### Dados não aparecem
1. Verifique o console do navegador (F12)
2. Confirme que o Flask está rodando
3. Teste o reprocessamento

### Erro de instalação
```bash
# Use o pip com --user se necessário
pip install --user -r requirements.txt

# Ou crie um ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Tecnologias Utilizadas

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Processamento**: PyPDF2
- **Interface**: Design responsivo com animações

## Licença

Sistema desenvolvido para análise educacional. Livre para uso e modificação conforme necessidades específicas.

## Suporte

Para dúvidas ou problemas:
1. Verifique este README
2. Consulte os comentários no código
3. Teste o reprocessamento dos PDFs
4. Verifique o formato dos arquivos PDF
