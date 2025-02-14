"# speech-to-text"

# Speech-to-Text App com Whisper, Flask e React

Este projeto realiza reconhecimento de fala localmente usando o modelo Whisper da OpenAI, com um backend em Python (Flask) e um frontend em React.

---

## **Pré-requisitos**

- **Python 3.9+** instalado
- **Node.js 16+** instalado
- **FFmpeg** instalado e no PATH
- **Make** instalado e no PATH

---

## **Configuração do Backend (Python)**

1. Navegue até a pasta `backend`:
   ```bash
   cd backend
   ```
2. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\\Scripts\\activate   # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Instale o Whisper e o Flask-CORS:
   ```bash
   pip install openai-whisper flask flask-cors
   ```
5. Adicione o caminho do `ffmpeg` ao PATH, caso necessário.
6. Execute o backend:
   ```bash
   python app.py
   ```
   O backend estará rodando em `http://127.0.0.1:5000`.

---

## **Configuração do Frontend (React)**

1. Navegue até a pasta `frontend`:
   ```bash
   cd frontend
   ```
2. Instale as dependências:
   ```bash
   npm install
   ```
3. Execute o frontend:
   ```bash
   npm start
   ```
   O frontend estará rodando em `http://localhost:3000`.

---

## **Fluxo do Projeto**

- O frontend grava o áudio, converte para MP3 e envia via `axios` para o backend.
- O backend recebe o áudio, salva temporariamente, processa com o Whisper e retorna o texto transcrito.

---

## **Possíveis Erros e Soluções**

- `FileNotFoundError`: Instale o `FFmpeg` e adicione ao PATH.
- `Network Error` no React: Configure o CORS no backend.
- `make` não encontrado: Instale o Make no Windows.

---

## **Comandos Úteis**

- Para instalar FFmpeg no Windows:
  ```bash
  winget install GnuWin32.Make
  choco install ffmpeg
  ```

Boa sorte e bons testes! 😊
