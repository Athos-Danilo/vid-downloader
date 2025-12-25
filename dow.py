import os
import sys
import re
import shutil
import socket
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from colorama import Fore, Style, init
from tqdm import tqdm
import subprocess

# Inicializa colorama
init(autoreset=True)

# Pasta de Downloads do usuário
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

# Barra de progresso única
barra_progresso = None

def menu():
    print(Fore.CYAN + Style.BRIGHT + "\n=== MENU YOUTUBE DOWNLOADER ===")
    print(Fore.YELLOW + "1 - Baixar vídeo")
    print(Fore.YELLOW + "2 - Baixar apenas áudio (MP3)")
    print(Fore.YELLOW + "3 - Listar opções de qualidade (vídeo+áudio)")
    print(Fore.YELLOW + "4 - Baixar playlist inteira (vídeo)")
    print(Fore.YELLOW + "5 - Baixar playlist inteira (áudio MP3)")
    print(Fore.YELLOW + "0 - Sair")

def listar_qualidades(url):
    print(Fore.GREEN + "\nListando opções de qualidade com ÁUDIO + VÍDEO...\n")
    try:
        ydl_opts = {
            'listformats': True,
            'quiet': True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    print(Fore.YELLOW + f"ID: {f['format_id']} | "
                          f"Resolução: {f.get('resolution','?')} | "
                          f"Extensão: {f['ext']} | "
                          f"Tamanho: {f.get('filesize','?')} | "
                          f"Vídeo: {f['vcodec']} | Áudio: {f['acodec']}")
        print(Fore.CYAN + Style.BRIGHT + "\nDigite o código do ID para escolher a qualidade.\n")
    except Exception as e:
        print(Fore.RED + f"Erro ao listar qualidades: {e}")

def progresso(d):
    global barra_progresso
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        baixado = d.get('downloaded_bytes', 0)
        if total:
            if barra_progresso is None:
                barra_progresso = tqdm(total=total, unit='B', unit_scale=True, desc="Baixando", leave=False)
            barra_progresso.total = total
            barra_progresso.n = baixado
            barra_progresso.refresh()
    elif d['status'] == 'finished':
        if barra_progresso is not None:
            barra_progresso.close()
            barra_progresso = None
        print(Fore.GREEN + Style.BRIGHT + "\nDownload concluído!")

def executar_download(ydl_opts, url, contexto="download"):
    global barra_progresso
    barra_progresso = None
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except DownloadError as e:
        print(Fore.RED + f"Erro durante {contexto}: {e}")
    except Exception as e:
        print(Fore.RED + f"Erro inesperado: {e}")

# Função de conversão com FFmpeg
def converter_video_mp4(caminho_arquivo):
    try:
        print(Fore.CYAN + "Convertendo vídeo para formato compatível...")
        arquivo_temp = caminho_arquivo.replace(".mp4", "_convertido.mp4")
        
        # Usar ffmpeg para converter
        cmd = [
            'ffmpeg',
            '-i', caminho_arquivo,
            '-c:v', 'libx264',
            '-crf', '18',
            '-c:a', 'aac',
            '-q:a', '100',
            '-y',  # Sobrescrever arquivo
            arquivo_temp
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        os.remove(caminho_arquivo)
        os.rename(arquivo_temp, caminho_arquivo)
        
        print(Fore.GREEN + "Conversão concluída e arquivo substituído!")
    except FileNotFoundError:
        print(Fore.YELLOW + "FFmpeg não encontrado. Instalando...")
        print(Fore.YELLOW + "Por favor, instale FFmpeg manualmente de: https://ffmpeg.org/download.html")
    except Exception as e:
        print(Fore.RED + f"Erro na conversão: {e}")

def baixar_video(url, itag=None):
    ydl_opts = {
        'progress_hooks': [progresso],
        'format': itag if itag else 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'noplaylist': True,
    }
    executar_download(ydl_opts, url, contexto="download de vídeo")

    try:
        with YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            nome_arquivo = os.path.join(DOWNLOAD_DIR, f"{info['title']}.mp4")
            if os.path.exists(nome_arquivo):
                converter_video_mp4(nome_arquivo)
    except Exception as e:
        print(Fore.RED + f"Não foi possível localizar o arquivo para conversão: {e}")

def baixar_audio(url):
    ydl_opts = {
        'progress_hooks': [progresso],
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': True,
    }
    executar_download(ydl_opts, url, contexto="download de áudio")

def baixar_playlist_video(url):
    ydl_opts = {
        'progress_hooks': [progresso],
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(playlist_title)s', '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'noplaylist': False,
        'ignoreerrors': True,
    }
    print(Fore.GREEN + "\nBaixando playlist inteira como vídeo...\n")
    executar_download(ydl_opts, url, contexto="download de playlist (vídeo)")

    try:
        with YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            for entry in info.get('entries', []):
                if entry:
                    nome_arquivo = os.path.join(DOWNLOAD_DIR, info['title'], f"{entry['title']}.mp4")
                    if os.path.exists(nome_arquivo):
                        converter_video_mp4(nome_arquivo)
    except Exception as e:
        print(Fore.RED + f"Erro ao converter vídeos da playlist: {e}")

def baixar_playlist_audio(url):
    ydl_opts = {
        'progress_hooks': [progresso],
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(playlist_title)s', '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'noplaylist': False,
        'ignoreerrors': True,
    }
    print(Fore.GREEN + "\nBaixando playlist inteira como áudio MP3...\n")
    executar_download(ydl_opts, url, contexto="download de playlist (áudio)")

def main():
    while True:
        menu()
        opcao = input(Fore.CYAN + Style.BRIGHT + "\nEscolha uma opção: ").strip()

        if opcao == "1":
            url = input(Fore.MAGENTA + "Digite a URL do vídeo: ").strip()
            listar_qualidades(url)
            itag = input(Fore.MAGENTA + "Digite o código do ID da qualidade desejada (ou Enter para padrão): ").strip()
            baixar_video(url, itag if itag else None)

        elif opcao == "2":
            url = input(Fore.MAGENTA + "Digite a URL do vídeo: ").strip()
            baixar_audio(url)

        elif opcao == "3":
            url = input(Fore.MAGENTA + "Digite a URL do vídeo: ").strip()
            listar_qualidades(url)

        elif opcao == "4":
            url = input(Fore.MAGENTA + "Digite a URL da playlist: ").strip()
            baixar_playlist_video(url)

        elif opcao == "5":
            url = input(Fore.MAGENTA + "Digite a URL da playlist: ").strip()
            baixar_playlist_audio(url)

        elif opcao == "0":
            print(Fore.RED + Style.BRIGHT + "\nSaindo... Até mais!")
            break

        else:
            print(Fore.RED + "Opção inválida, tente novamente!")

if __name__ == "__main__":
    main()