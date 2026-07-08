# Gerador de Contrato – Penteado e Make

App web simples para a dona do salão preencher os dados da cliente e gerar o
contrato de prestação de serviço em PDF, no mesmo modelo usado atualmente.

## Como funciona

1. A dona do salão acessa o link do app pelo navegador (computador ou celular).
2. Digita a senha de acesso.
3. Preenche nome, CPF, RG, evento, data e valores da cliente.
4. Clica em "Gerar contrato em PDF" e baixa o arquivo pronto para assinatura.

Os dados da contratada (Ana Maria Ristoff) já ficam fixos no sistema — só é
necessário alterá-los em [app.py](app.py) se algum dado dela mudar.

## Rodando localmente (para testes)

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
# edite .streamlit\secrets.toml e defina sua senha
.\.venv\Scripts\python -m streamlit run app.py
```

## Publicando de graça no Streamlit Community Cloud

1. Crie uma conta gratuita em https://streamlit.io/cloud (pode entrar com GitHub).
2. Suba este projeto para um repositório no GitHub (pode ser privado).
   - **Importante:** o arquivo `.streamlit/secrets.toml` não deve ser enviado
     ao GitHub (o `.gitignore` já cuida disso).
3. No painel do Streamlit Cloud, clique em "New app", escolha o repositório e
   o arquivo `app.py`.
4. Antes de publicar (ou depois, em *Settings → Secrets*), adicione a senha:
   ```toml
   app_password = "sua-senha-aqui"
   ```
5. Publique. Você receberá um link (ex: `https://seu-app.streamlit.app`) para
   enviar à dona do salão — pode até salvar como atalho na tela inicial do
   celular dela.

Por ser o plano gratuito, o app "dorme" depois de um tempo sem uso e demora
cerca de 30–60 segundos para acordar no primeiro acesso do dia. Isso não
gera nenhum custo e é o esperado para esse volume de uso.

## Estrutura do projeto

- [app.py](app.py) — interface (formulário, login, dados fixos da contratada).
- [pdf_generator.py](pdf_generator.py) — monta o PDF do contrato com ReportLab.
- [requirements.txt](requirements.txt) — dependências Python.
- `.streamlit/secrets.toml` — senha de acesso (local, não vai para o Git).
