# GeneXus Launcher 🚀

Uma ferramenta poderosa e intuitiva para desenvolvedores GeneXus gerenciarem múltiplas instalações e versões de forma organizada e eficiente.

<p align="center">
  <img src="AppIcon.png" alt="GeneXus Launcher" width="128">
</p>

## ✨ Funcionalidades

- **Gerenciamento Multi-Instância**: Cadastre e organize todas as suas pastas do GeneXus em uma lista única.
- **Início Limpo (Clean & Start)**: Automatiza o processo de limpeza (exclusão de `.gxmodules` e execução do `/install`) antes de abrir a IDE.
- **Validação de Instâncias**: Detecta se existem instâncias de versões diferentes rodando para evitar conflitos de cache e binários.
- **Persistência Inteligente**: O launcher lembra qual foi a última versão que você utilizou e a deixa pré-selecionada ao abrir o aplicativo.
- **Extração Automática de Ícones**: Identifica e exibe o ícone original de cada versão do GeneXus na listagem.
- **License Manager**: Acesso rápido ao gerenciador de licenças de cada instalação específica.
- **Prevenção de Duplicidade**: Sistema de validação que impede o cadastro duplicado da mesma pasta de instalação.

## 🛠️ Tecnologias Utilizadas

- **Python 3**: Linguagem base do projeto.
- **Tkinter/Ttk**: Interface gráfica nativa e leve.
- **PowerShell Integration**: Para detecção precisa de processos e manipulação do sistema Windows.
- **Hashlib (MD5)**: Para identificação única e persistência segura das configurações.

## 🚀 Como Executar

Se você estiver rodando a partir do código fonte:

1. Certifique-se de ter o Python instalado.
2. Execute o arquivo principal:
   ```bash
   python start_Genexus.py
   ```

## 📦 Compilação (Gerar .exe)

O projeto inclui um script de compilação em PowerShell (`compilar.ps1`) que utiliza o PyInstaller para gerar um executável único (`onefile`) com todos os recursos embutidos.

```powershell
./compilar.ps1
```

## 📝 Notas de Versão

- **v1.24**: Adicionada persistência da última versão selecionada via Hash MD5 e validação de caminhos duplicados.
- **v1.23**: Implementada reordenação de itens na lista e extração de ícones em tempo de execução.

---
Desenvolvido por **Igor Menin**
