# YouTube Downloader (vid-downloader)

Pequeno utilitário em Python para baixar vídeos/áudios do YouTube usando `yt_dlp` e converter para MP4 com `ffmpeg`.

**Funcionalidades principais**
- Baixar vídeo (opção de escolher formato via ID)
- Baixar apenas áudio (MP3)
- Listar formatos disponíveis (vídeo + áudio)
- Baixar playlist inteira (vídeo ou áudio)
- Conversão automática pós-download para MP4 (H.264 + AAC, CRF 18)

**Arquivo principal**: [dow.py](dow.py)

Requisitos
- Windows (instruções abaixo para Windows)
- Python 3.10+ (recomendado)
- FFmpeg instalado e disponível no PATH

Dependências Python (instalar no venv do projeto)
- yt_dlp
- colorama
- tqdm
- ffmpeg-python

Instalação (Windows)
1. Ative o virtualenv (se existir) ou crie um:

```powershell
# Ativar (se já existir .venv)
& "./.venv/Scripts/Activate.ps1"

# Ou criar e ativar
python -m venv .venv
& "./.venv/Scripts/Activate.ps1"
```

2. Instale dependências:

```powershell
python -m pip install yt_dlp colorama tqdm ffmpeg-python
```

3. Instale o FFmpeg (necessário para conversão):
- Via winget:

```powershell
winget install ffmpeg
```

- Ou via Chocolatey:

```powershell
choco install ffmpeg -y
```

- Ou baixe manualmente: https://ffmpeg.org/download.html

Uso

```powershell
& "C:/Users/Athos/ADS/Meus Projetos/vid-downloader/.venv/Scripts/python.exe" dow.py
```

Siga o menu interativo:
- `1` - Baixar vídeo (após o download, o script converte automaticamente para MP4 se o FFmpeg estiver disponível)
- `2` - Baixar apenas áudio (MP3)
- `3` - Listar formatos disponíveis
- `4` - Baixar playlist inteira (vídeo)
- `5` - Baixar playlist inteira (áudio MP3)

Conversão automática
- Formato de saída: MP4
- Vídeo: H.264 (`libx264`)
- Áudio: AAC
- Qualidade atual: CRF 18 (alta qualidade)

Alterar qualidade
- Edite a função `converter_video_mp4` em [dow.py](dow.py) e altere o valor `-crf` para o desejado (menor = melhor qualidade). Ex.: CRF 15 para ainda mais qualidade.

Observações
- Se o FFmpeg não estiver no PATH, a conversão falhará; instale-o conforme instruções acima.
- Para sistemas Linux/macOS, os passos são análogos (instale FFmpeg via apt/brew etc.).

Precisa que eu adicione um `requirements.txt` ou que eu ajuste o CRF padrão?