"""Gera o PDF do contrato de prestação de serviço (penteado e make)."""

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

CLAUSULAS = [
    (
        "1. OBJETO",
        "O presente contrato tem como objeto a prestação de serviços de penteado e "
        "maquiagem para {papel_evento}, incluindo prévia de penteado e maquiagem em "
        "data previamente acordada entre as partes.",
    ),
    (
        "2. VALOR E FORMA DE PAGAMENTO",
        "O valor total do serviço é de {valor_total}, sendo {valor_sinal} pagos a "
        "título de sinal, {status_sinal}, e o saldo restante até a data do evento.",
    ),
    (
        "3. RESERVA DE DATA",
        "A reserva da data somente será garantida após a confirmação do pagamento "
        "do sinal.",
    ),
    (
        "4. CANCELAMENTO",
        "Em caso de cancelamento por parte da contratante, o valor pago a título "
        "de sinal não será devolvido.",
    ),
    (
        "5. REAGENDAMENTO",
        "Solicitações de reagendamento estarão sujeitas à disponibilidade da "
        "profissional.",
    ),
    (
        "6. ATRASOS",
        "A contratante compromete-se a respeitar o horário previamente acordado.",
    ),
    (
        "7. DESLOCAMENTO",
        "Caso haja necessidade de deslocamento, poderá ser cobrada taxa adicional "
        "previamente informada.",
    ),
    (
        "8. ACEITAÇÃO",
        "O pagamento do sinal implica na aceitação integral de todas as cláusulas "
        "deste contrato.",
    ),
    (
        "9. HIGIENE DO CABELO",
        "A contratante deve comparecer com o cabelo limpo e seco.",
    ),
    (
        "10. CONVIDADOS",
        "Caso haja convidados adicionais contratando procedimento de penteado "
        "e/ou maquiagem, seus nomes, procedimentos e valores constam na lista "
        "anexa a este contrato, sujeitos às mesmas condições aqui "
        "estabelecidas.",
    ),
]


def _formatar_moeda(valor: float) -> str:
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def gerar_contrato_pdf(dados: dict) -> BytesIO:
    """Recebe os dados do formulário e devolve o PDF em memória (BytesIO)."""

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        "TituloContrato",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=16,
    )
    cabecalho_style = ParagraphStyle(
        "CabecalhoTabela", parent=styles["Normal"], fontName="Helvetica-Bold"
    )
    campo_style = ParagraphStyle("Campo", parent=styles["Normal"], leading=14)
    clausula_titulo_style = ParagraphStyle(
        "ClausulaTitulo",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        spaceBefore=10,
        spaceAfter=4,
    )
    clausula_texto_style = ParagraphStyle(
        "ClausulaTexto", parent=styles["Normal"], alignment=TA_JUSTIFY, leading=14
    )

    elementos = []

    elementos.append(
        Paragraph("CONTRATO DE PRESTAÇÃO DE SERVIÇO – PENTEADO E MAKE", titulo_style)
    )
    elementos.append(Spacer(1, 0.8 * cm))

    contratante_linhas = [
        f"Nome: {dados['contratante_nome']}",
        f"CPF: {dados['contratante_cpf']}",
        f"RG: {dados['contratante_rg']}",
        f"Evento: {dados['evento']}",
        f"Papel no evento: {dados['papel_evento']}",
        f"Data: {dados['data_evento']}",
    ]
    nome_homenageada = dados.get("nome_homenageada", "").strip()
    if nome_homenageada and nome_homenageada != dados["contratante_nome"]:
        contratante_linhas.append(
            f"Nome de quem recebe o serviço principal: {nome_homenageada}"
        )
    contratante_html = "<br/>".join(contratante_linhas)
    contratada_html = (
        f"Nome: {dados['contratada_nome']}<br/>"
        f"CPF: {dados['contratada_cpf']}<br/>"
        f"Profissão: {dados['contratada_profissao']}"
    )

    tabela_dados = [
        [Paragraph("CONTRATANTE", cabecalho_style), Paragraph("CONTRATADA", cabecalho_style)],
        [Paragraph(contratante_html, campo_style), Paragraph(contratada_html, campo_style)],
    ]
    tabela = Table(tabela_dados, colWidths=[8.3 * cm, 8.3 * cm])
    tabela.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.75, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elementos.append(tabela)
    elementos.append(Spacer(1, 0.8 * cm))

    status_sinal = "já quitados" if dados["sinal_pago"] else "a serem pagos na confirmação"
    contexto_clausulas = {
        "papel_evento": dados["papel_evento"].lower(),
        "valor_total": _formatar_moeda(dados["valor_total"]),
        "valor_sinal": _formatar_moeda(dados["valor_sinal"]),
        "status_sinal": status_sinal,
    }

    for titulo, texto in CLAUSULAS:
        elementos.append(Paragraph(titulo, clausula_titulo_style))
        elementos.append(Paragraph(texto.format(**contexto_clausulas), clausula_texto_style))

    convidados = dados.get("convidados", [])
    if convidados:
        elementos.append(Spacer(1, 0.4 * cm))
        elementos.append(Paragraph("ANEXO – CONVIDADOS COM PROCEDIMENTO", clausula_titulo_style))

        linhas_convidados = [
            [
                Paragraph("Nome", cabecalho_style),
                Paragraph("Procedimento", cabecalho_style),
                Paragraph("Valor", cabecalho_style),
            ]
        ]
        for convidado in convidados:
            procedimentos_texto = ", ".join(convidado.get("procedimentos", [])) or "-"
            linhas_convidados.append(
                [
                    Paragraph(convidado["nome"], campo_style),
                    Paragraph(procedimentos_texto, campo_style),
                    Paragraph(_formatar_moeda(convidado.get("valor", 0.0)), campo_style),
                ]
            )

        tabela_convidados = Table(linhas_convidados, colWidths=[7 * cm, 5.6 * cm, 4 * cm])
        tabela_convidados.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
                    ("INNERGRID", (0, 0), (-1, -1), 0.75, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elementos.append(tabela_convidados)

    elementos.append(Spacer(1, 2 * cm))

    assinatura_tabela = Table(
        [
            ["_" * 40, "_" * 40],
            [dados["contratante_nome"], dados["contratada_nome"]],
            [f"CPF: {dados['contratante_cpf']}", f"CPF: {dados['contratada_cpf']}"],
        ],
        colWidths=[8.3 * cm, 8.3 * cm],
    )
    assinatura_tabela.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("TOPPADDING", (0, 0), (-1, 0), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    elementos.append(assinatura_tabela)

    doc.build(elementos)
    buffer.seek(0)
    return buffer
