#!/usr/bin/env python
"""
Script para automatizar a geração e atualização das chaves VAPID.

Este script irá:
1. Gerar um novo par de chaves VAPID (pública e privada) usando o script 'gerar_chaves_vapid.py'.
2. Inserir a chave privada diretamente no arquivo settings.py.
3. Inserir a chave pública diretamente no arquivo pushNotifications.ts do frontend.

Execute: python automatizar_chaves.py
"""

import os
import re
import sys
from pathlib import Path

# Importa a função de geração de chaves do seu script existente
try:
    from gerar_chaves_vapid import generate_vapid_keys
except ImportError:
    print("❌ Erro: O arquivo 'gerar_chaves_vapid.py' não foi encontrado.")
    print("   Certifique-se de que este script está na mesma pasta que 'gerar_chaves_vapid.py'.")
    sys.exit(1)

# --- Definição dos Caminhos ---
BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PY_PATH = BASE_DIR / 'sistema_gestao' / 'settings.py'
FRONTEND_DIR = BASE_DIR.parent / 'frontend'
PUSH_TS_PATH = FRONTEND_DIR / 'src' / 'services' / 'pushNotifications.ts'

def update_file_content(file_path: Path, pattern: str, replacement: str):
    """
    Lê um arquivo, substitui um padrão por um novo conteúdo e salva o arquivo.
    """
    if not file_path.exists():
        print(f"⚠️  Aviso: Arquivo não encontrado em '{file_path}'. Pulando atualização.")
        return False

    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Verifica se o padrão foi encontrado
        if not re.search(pattern, content, flags=re.DOTALL):
            print(f"⚠️  Aviso: Padrão de chave não encontrado em '{file_path.name}'.")
            print("   A estrutura do arquivo pode ter mudado. Verifique manualmente.")
            return False
            
        new_content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
        file_path.write_text(new_content, encoding='utf-8')
        print(f"✅ Arquivo '{file_path.name}' atualizado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao atualizar o arquivo '{file_path.name}': {e}")
        return False

def main():
    print("=" * 70)
    print("🚀 Automatizando a Geração e Atualização de Chaves VAPID")
    print("=" * 70)
    
    # 1. Gerar novas chaves
    print("\n1. Gerando novo par de chaves VAPID...")
    private_key, public_key = generate_vapid_keys()
    
    if not private_key or not public_key:
        print("\nProcesso abortado devido a erro na geração de chaves.")
        sys.exit(1)
        
    print("   Chaves geradas com sucesso.")
    
    # 2. Atualizar settings.py com a chave privada
    print("\n2. Atualizando a chave privada no backend (settings.py)...")
    # Padrão para encontrar o bloco VAPID_PRIVATE_KEY
    private_key_pattern = r'(VAPID_PRIVATE_KEY\s*=\s*""").*?(""".strip())'
    # Conteúdo que irá substituir o padrão, com a nova chave
    private_key_replacement = f'\\1\n{private_key}\n\\2'
    update_file_content(SETTINGS_PY_PATH, private_key_pattern, private_key_replacement)

    # 3. Atualizar pushNotifications.ts com a chave pública
    print("\n3. Atualizando a chave pública no frontend (pushNotifications.ts)...")
    # Padrão para encontrar a applicationServerKey
    public_key_pattern = r"(const applicationServerKey\s*=\s*this\.urlBase64ToUint8Array\(\s*['\"])([^'\"]+)(['\"])"
    # Conteúdo que irá substituir o padrão, com a nova chave
    public_key_replacement = f'\\1{public_key}\\3'
    update_file_content(PUSH_TS_PATH, public_key_pattern, public_key_replacement)
    
    print("\n" + "=" * 70)
    print("🎉 Processo Concluído!")
    print("=" * 70)
    print("\n💡 Próximos Passos:")
    print("   1. Pare todos os servidores (Backend, QCluster, Frontend).")
    print("   2. Reinicie-os para que as novas chaves sejam carregadas.")
    print("\n   Lembre-se de reiniciar:")
    print("   - Servidor Django: python manage.py runserver")
    print("   - QCluster: python manage.py qcluster")
    print("   - Servidor Frontend: npm run dev (ou similar)")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()