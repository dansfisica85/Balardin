# 🚀 Deploy no Vercel - Instruções Passo a Passo

## ✅ Status do Projeto
- [x] Código configurado para site estático
- [x] `vercel.json` criado e configurado
- [x] Dados JSON compilados disponíveis
- [x] Interface responsiva funcionando
- [x] Testado localmente com sucesso

## 📋 Próximos Passos para Deploy

### 1. Conectar ao Vercel
1. Acesse [vercel.com](https://vercel.com)
2. Faça login com sua conta GitHub
3. Clique em "New Project"
4. Selecione o repositório `Balardin`

### 2. Configuração do Deploy
- **Framework Preset**: Other
- **Root Directory**: `./` (raiz do projeto)
- **Build Command**: (deixe vazio - site estático)
- **Output Directory**: `./` (raiz do projeto)

### 3. Deploy Automático
- O Vercel detectará automaticamente o `vercel.json`
- Deploy será iniciado automaticamente
- URL será gerada: `https://balardin-xxx.vercel.app`

### 4. Configuração de Domínio (Opcional)
- Vá em Settings > Domains
- Adicione domínio customizado se desejar

## 🔧 Arquivos Importantes

### `/vercel.json`
```json
{
  "version": 2,
  "public": true,
  "trailingSlash": false,
  "cleanUrls": true,
  "headers": [...],
  "rewrites": [...]
}
```

### Estrutura Final
```
Balardin/
├── index.html              ✅ Página principal
├── css/style.css           ✅ Estilos
├── js/script.js            ✅ JavaScript
├── data/alunos_compilado.json ✅ Dados
├── vercel.json             ✅ Configuração Vercel
└── *.pdf                   ✅ Arquivos originais
```

## 🌐 URLs de Acesso

### Desenvolvimento Local
```bash
python -m http.server 8000
# http://localhost:8000
```

### Produção (após deploy)
- **Vercel**: `https://balardin-xxx.vercel.app`
- **Domínio Custom**: (se configurado)

## ⚡ Features Configuradas

- ✅ Site 100% estático (sem backend)
- ✅ Carregamento rápido de dados via JSON
- ✅ Interface responsiva
- ✅ Dropdowns dinâmicos
- ✅ Relatórios por risco
- ✅ Alertas visuais automáticos
- ✅ Cache otimizado
- ✅ Headers corretos para JSON

## 🎯 Funcionalidades Principais

1. **Busca Individual**
   - Dropdown de turmas (1A, 1B, 2A, etc.)
   - Seleção de série/ano
   - Busca específica por aluno

2. **Relatórios de Risco**
   - Notas baixas (< 5.0)
   - Frequência baixa (< 75%)
   - Relatório combinado

3. **Interface Intuitiva**
   - Design moderno e responsivo
   - Alertas visuais coloridos
   - Animações sutis

## 🔍 Verificação Pós-Deploy

Após o deploy, teste:
1. ✅ Carregamento da página principal
2. ✅ Funcionamento dos dropdowns
3. ✅ Busca individual de alunos
4. ✅ Geração de relatórios
5. ✅ Responsividade mobile
6. ✅ Carregamento dos dados JSON

## 🆘 Troubleshooting

### Erro 404 no JSON
- Verifique se `data/alunos_compilado.json` existe
- Confirme que o path está correto no `js/script.js`

### Interface quebrada
- Verifique se `css/style.css` e `js/script.js` carregam
- Teste o console do navegador (F12)

### Deploy falha
- Confirme que `vercel.json` está na raiz
- Verifique os logs no dashboard do Vercel

---

**🎉 Seu sistema LIVIA está pronto para rodar no Vercel!**
