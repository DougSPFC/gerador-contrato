# CLAUDE.md

Este arquivo fornece contexto para o Claude Code (claude.ai/code) ao trabalhar neste repositório.

## Visão geral do projeto

Gerador de contrato de prestação de serviço (penteado e make) para um salão de
beleza. A dona do salão preenche um formulário web com os dados da cliente
(contratante) e o app gera um PDF do contrato pronto para assinatura, seguindo
o modelo em `contrato_noiva_irene.pdf` (fornecido como referência de layout).

## Stack técnica

- Python, Streamlit (interface web) e ReportLab (geração de PDF).
- Sem banco de dados — cada contrato é gerado sob demanda e baixado pelo navegador.

## Comandos úteis

- Instalar dependências: `.\.venv\Scripts\pip install -r requirements.txt`
- Rodar localmente: `.\.venv\Scripts\python -m streamlit run app.py`

## Estrutura do projeto

- [app.py](app.py) — formulário, login por senha e dados fixos da contratada (Ana Maria Ristoff).
- [pdf_generator.py](pdf_generator.py) — monta o layout do PDF (cláusulas fixas + dados variáveis).
- `.streamlit/secrets.toml` — senha de acesso e CPF da contratada (nunca commitar; ver `.streamlit/secrets.toml.example`).

## Convenções de código

- Textos e nomes de variáveis em português, consistente com o domínio (contrato brasileiro).
- Dados fixos da contratada (nome, profissão) ficam como constantes no topo de `app.py`, não em formulário.
  O CPF, por ser dado sensível, fica em `st.secrets["contratada_cpf"]` — o repositório GitHub é público.
- Cláusulas do contrato ficam centralizadas na lista `CLAUSULAS` em `pdf_generator.py`.

## Notas adicionais

- Deploy recomendado: Streamlit Community Cloud (gratuito). Ver [README.md](README.md) para o passo a passo.
- Se a dona do salão pedir novas cláusulas ou campos (ex: outro tipo de evento,
  outro profissional), ajustar `CLAUSULAS`/formulário em vez de criar um segundo app.
