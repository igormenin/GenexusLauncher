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
- **Atualização Automática**: Sistema de upgrade obrigatório integrado ao GitHub para garantir que todos os usuários estejam sempre na versão mais recente.


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

## 🔄 Fluxo de Atualização (CI/CD)

O projeto utiliza **GitHub Actions** para automatizar o build e a distribuição:

1. **Gatilho**: O build é disparado ao enviar uma tag Git (ex: `v1.25`) para o repositório.
2. **Build**: O GitHub Actions compila o `.exe` usando PyInstaller em um ambiente Windows.
3. **Release**: Um arquivo `last_version.zip` é gerado e anexado à Release do GitHub.
4. **Distribuição**: O aplicativo local detecta a nova versão, baixa o pacote e se auto-atualiza automaticamente.

Para lançar uma nova versão:
```bash
git tag v1.XX
git push origin v1.XX
```


## 📝 Notas de Versão

- **v1.25**: Implementado sistema de atualização automática via GitHub e build automatizado com GitHub Actions. Adicionado modal de loading com fundo transparente.
- **v1.24**: Adicionada persistência da última versão selecionada via Hash MD5 e validação de caminhos duplicados.

- **v1.23**: Implementada reordenação de itens na lista e extração de ícones em tempo de execução.

---
Desenvolvido por **Igor Menin**
