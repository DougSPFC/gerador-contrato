"""App Streamlit para gerar contratos de prestação de serviço (penteado e make)."""

import uuid
from datetime import date

import streamlit as st

from pdf_generator import gerar_contrato_pdf

PROCEDIMENTOS = ["Penteado", "Maquiagem"]
MAX_CONVIDADOS = 5

# Dados fixos da contratada (profissional/salão). Edite aqui se mudar.
# O CPF fica em st.secrets (não vai para o repositório público no GitHub).
CONTRATADA_NOME = "Ana Maria Ristoff"
CONTRATADA_PROFISSAO = "Profissional de Penteado e Maquiagem"

EVENTOS = ["Casamento", "Debutante (15 anos)", "Formatura", "Ensaio Fotográfico", "Outro"]
PAPEIS = ["Noiva", "Madrinha", "Debutante", "Formanda", "Convidada", "Outro"]

st.set_page_config(page_title="Gerador de Contrato", page_icon="💇‍♀️")


def checar_senha() -> bool:
    """Mostra um formulário de login e retorna True se a senha estiver correta."""

    if st.session_state.get("autenticado"):
        return True

    st.title("Acesso restrito")
    senha_digitada = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        senha_correta = st.secrets.get("app_password")
        if senha_digitada and senha_digitada == senha_correta:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    return False


if not checar_senha():
    st.stop()

st.title("Gerador de Contrato – Penteado e Make")
st.caption("Preencha os dados da cliente para gerar o contrato em PDF.")

st.subheader("Convidados com procedimento (opcional)")
st.caption(
    "Use quando outras pessoas (além da contratante/homenageada) também vão "
    "fazer penteado e/ou maquiagem no mesmo contrato."
)

if "convidados" not in st.session_state:
    st.session_state["convidados"] = []


def _adicionar_convidado() -> None:
    st.session_state["convidados"].append(uuid.uuid4().hex)


def _remover_convidado(convidado_id: str) -> None:
    st.session_state["convidados"].remove(convidado_id)
    for campo in ("nome", "procedimentos", "valor"):
        st.session_state.pop(f"convidado_{campo}_{convidado_id}", None)


for convidado_id in list(st.session_state["convidados"]):
    col_nome, col_proc, col_valor, col_remover = st.columns([3, 3, 2, 1])
    with col_nome:
        st.text_input(
            "Nome",
            key=f"convidado_nome_{convidado_id}",
            label_visibility="collapsed",
            placeholder="Nome do convidado",
        )
    with col_proc:
        st.multiselect(
            "Procedimento",
            PROCEDIMENTOS,
            key=f"convidado_procedimentos_{convidado_id}",
            label_visibility="collapsed",
            placeholder="Procedimento",
        )
    with col_valor:
        st.number_input(
            "Valor (R$)",
            min_value=0.0,
            step=25.0,
            format="%.2f",
            key=f"convidado_valor_{convidado_id}",
            label_visibility="collapsed",
        )
    with col_remover:
        st.button(
            "🗑️",
            key=f"convidado_remover_{convidado_id}",
            on_click=_remover_convidado,
            args=(convidado_id,),
            help="Remover convidado",
        )

if len(st.session_state["convidados"]) < MAX_CONVIDADOS:
    st.button("+ Adicionar convidado", on_click=_adicionar_convidado)
else:
    st.caption(f"Limite de {MAX_CONVIDADOS} convidados por contrato.")

with st.form("dados_contrato"):
    st.subheader("Dados da contratante")
    contratante_nome = st.text_input("Nome completo")
    col1, col2 = st.columns(2)
    with col1:
        contratante_cpf = st.text_input("CPF", placeholder="000.000.000-00")
    with col2:
        contratante_rg = st.text_input("RG")

    nome_homenageada = st.text_input(
        "Nome de quem vai receber o serviço principal (se diferente da contratante)",
        placeholder="Ex: nome da debutante ou da noiva, quando quem preenche é a mãe/responsável",
    )

    col3, col4 = st.columns(2)
    with col3:
        evento = st.selectbox("Evento", EVENTOS)
    with col4:
        papel_evento = st.selectbox("Papel no evento", PAPEIS)

    data_evento = st.date_input("Data do evento", value=date.today(), format="DD/MM/YYYY")

    st.subheader("Valores")
    col5, col6 = st.columns(2)
    with col5:
        valor_total = st.number_input("Valor total (R$)", min_value=0.0, step=50.0, format="%.2f")
    with col6:
        valor_sinal = st.number_input("Valor do sinal (R$)", min_value=0.0, step=50.0, format="%.2f")

    sinal_pago = st.checkbox("Sinal já foi pago", value=True)

    enviado = st.form_submit_button("Gerar contrato em PDF")

if enviado:
    campos_obrigatorios = {
        "Nome completo": contratante_nome,
        "CPF": contratante_cpf,
        "RG": contratante_rg,
    }
    faltando = [nome for nome, valor in campos_obrigatorios.items() if not valor.strip()]

    if valor_sinal > valor_total:
        st.error("O valor do sinal não pode ser maior que o valor total.")
    elif faltando:
        st.error(f"Preencha os campos obrigatórios: {', '.join(faltando)}.")
    else:
        convidados = []
        for convidado_id in st.session_state["convidados"]:
            nome_convidado = st.session_state.get(f"convidado_nome_{convidado_id}", "").strip()
            if not nome_convidado:
                continue
            convidados.append(
                {
                    "nome": nome_convidado,
                    "procedimentos": st.session_state.get(
                        f"convidado_procedimentos_{convidado_id}", []
                    ),
                    "valor": st.session_state.get(f"convidado_valor_{convidado_id}", 0.0),
                }
            )

        dados = {
            "contratante_nome": contratante_nome.strip(),
            "contratante_cpf": contratante_cpf.strip(),
            "contratante_rg": contratante_rg.strip(),
            "nome_homenageada": nome_homenageada.strip(),
            "convidados": convidados,
            "evento": evento,
            "papel_evento": papel_evento,
            "data_evento": data_evento.strftime("%d/%m/%Y"),
            "valor_total": valor_total,
            "valor_sinal": valor_sinal,
            "sinal_pago": sinal_pago,
            "contratada_nome": CONTRATADA_NOME,
            "contratada_cpf": st.secrets["contratada_cpf"],
            "contratada_profissao": CONTRATADA_PROFISSAO,
        }
        pdf_buffer = gerar_contrato_pdf(dados)
        nome_arquivo = f"contrato_{contratante_nome.strip().replace(' ', '_').lower()}.pdf"

        st.success("Contrato gerado com sucesso!")
        st.download_button(
            "Baixar contrato em PDF",
            data=pdf_buffer,
            file_name=nome_arquivo,
            mime="application/pdf",
        )
