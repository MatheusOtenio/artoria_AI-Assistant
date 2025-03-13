# Assistente Virtual

![Interface Demo](demo.png) <!-- Adicione uma imagem da interface se disponível -->

## Introdução

O Assistente Virtual é uma aplicação desktop com interface gráfica que combina capacidades de chat inteligente com processamento de documentos PDF. Desenvolvido em Python, oferece:

- Interação com modelos de linguagem via API Ollama local
- Extração e análise de texto de arquivos PDF
- Histórico de conversas persistente
- Sistema de cache para respostas frequentes
- Interface intuitiva com suporte a multitarefa assíncrona

## Estrutura do Projeto

| Arquivo            | Descrição                                                            |
| ------------------ | -------------------------------------------------------------------- |
| `assistente.py`    | Código principal com interface gráfica e lógica de funcionamento     |
| `chat_history.txt` | Armazena todo o histórico de conversas em formato texto              |
| `chat_cache.db`    | Banco de dados SQLite para cache de perguntas e respostas frequentes |
| `README.md`        | Documentação do projeto (este arquivo)                               |

## Instalação

1. **Pré-requisitos**:

   - Python 3.8+
   - [Ollama](https://ollama.ai/) instalado e rodando localmente
   - Modelo DeepSeek R1-7B instalado: `ollama pull deepseek-r1:7b`

2. Instalar dependências:
   ```bash
   pip install -r requirements.txt
   ```

Conteúdo do requirements.txt:

Copy
aiohttp>=3.9.3
PyMuPDF>=1.23.8

Uso
Iniciar o aplicativo:
python assistente.py

Funcionalidades principais:

Chat: Digite sua mensagem e clique em "Enviar" ou pressione Enter

PDF: Clique em "Abrir PDF" para extrair texto de documentos

Limpar: Use o comando /limpar ou botão dedicado para reiniciar a conversa

Histórico: As conversas são mantidas automaticamente entre sessões

Atalhos:

Enter: Envia mensagem

Shift+Enter: Nova linha na caixa de texto

Ctrl+O (Windows/Linux) ou Cmd+O (macOS): Abrir diálogo de arquivo PDF

Requisitos
Sistema Operacional: Windows 10+, macOS 12+, ou distribuição Linux moderna

Hardware Mínimo:

8GB RAM

4GB de espaço livre em disco

Conexão internet para API Ollama

Dependências Python:

aiohttp: Para comunicação assíncrona com a API Ollama

PyMuPDF: Biblioteca de processamento de PDFs

tkinter: Interface gráfica padrão do Python

**Nota:** Este README assume que o Ollama está configurado e rodando na porta padrão 11434. Para configurações personalizadas, ajuste a URL da API no arquivo `assistente.py`.
