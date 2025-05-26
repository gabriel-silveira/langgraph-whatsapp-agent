import os


def read_markdown_files(caminho_pasta):
    conteudos_markdown = []

    # Percorre todos os arquivos na pasta
    for nome_arquivo in os.listdir(caminho_pasta):
        if nome_arquivo.endswith('.md'):
            caminho_completo = os.path.join(caminho_pasta, nome_arquivo)
            try:
                with open(caminho_completo, 'r', encoding='utf-8') as arquivo:
                    conteudo = arquivo.read()
                    conteudos_markdown.append(conteudo)
            except Exception as e:
                print(f"Erro ao ler {nome_arquivo}: {e}")
    
    return conteudos_markdown
