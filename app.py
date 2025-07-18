from flask import Flask, render_template, request, send_file, jsonify
from fpdf import FPDF
from datetime import datetime
import os
from fpdf.enums import XPos, YPos

app = Flask(__name__)

# Dados fixos dos advogados
DADOS_ADVOGADOS = {
    "TIAGO": {
        "nome": "TIAGO LACHESKI SILVEIRA DE OLIVEIRA",
        "estado_civil": "casado",
        "profissao": "advogado",
        "cpf": "017.353.012-56",
        "rg": "13.437.948-0",
        "orgao_emissor": "SESP/PR",
        "oab": ["102.510", "11.124"],  # OAB/PR e OAB/RO
    },
    "THAYRONE": {
        "nome": "THAYRONE DANIEL ROSA SANTOS",
        "estado_civil": "solteiro",
        "profissao": "advogado",
        "cpf": "025.586.412-47",
        "rg": "não informado",
        "orgao_emissor": "SSPRO",
        "oab": ["15.231"],  # Apenas OAB/RO
    },
    "SEBASTIÃO": {
        "nome": "SEBASTIÃO BRINATI LOPES SIMIQUELI",
        "estado_civil": "solteiro",
        "profissao": "advogado",
        "cpf": "003.698.752-22",
        "rg": "1877906",
        "orgao_emissor": "SSPRO",
        "oab": ["14.719"],  # Apenas OAB/RO
    }
}

ENDERECO_ADV = "Av. Tancredo Neves nº 2.871, Bairro Centro, Machadinho D'Oeste/RO, CEP 76.868-000"


def header(pdf):
    logo_width = 60
    page_width = pdf.w
    x_pos = (page_width - logo_width) / 2
    pdf.image('static/images/logolacheski.png', x=x_pos, y=8, w=logo_width)


def formatar_cpf(cpf_num):
    cpf_num = ''.join(filter(str.isdigit, cpf_num))
    return f"{cpf_num[:3]}.{cpf_num[3:6]}.{cpf_num[6:9]}-{cpf_num[9:]}"


def gerar_procuracao(dados_cliente, incluir_thayrone, incluir_sebastiao):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_margins(left=30, top=30, right=20)

    # Adiciona o cabeçalho com a logo
    header(pdf)

    # Configuração de fonte e espaçamento
    pdf.set_font("Times", size=12)

    # Header
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 22, "P R O C U R A Ç Ã O", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(5)

    # Outorgante
    pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 7, "OUTORGANTE:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Times", size=12)

    texto_outorgante = f"{dados_cliente['nome_completo']}, brasileiro(a), {dados_cliente['estado_civil']}(a), {dados_cliente['profissao']}, devidamente inscrito(a) no CPF n.º {dados_cliente['cpf']}, residente e domiciliado(a) à {dados_cliente['endereco']}"

    pdf.set_x(37.5)
    pdf.multi_cell(0, 7, texto_outorgante)
    pdf.ln(5)

    # Outorgado
    pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 7, "OUTORGADO:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Times", size=12)

    advogados_selecionados = [DADOS_ADVOGADOS["TIAGO"]]

    if incluir_thayrone:
        advogados_selecionados.append(DADOS_ADVOGADOS["THAYRONE"])

    if incluir_sebastiao:
        advogados_selecionados.append(DADOS_ADVOGADOS["SEBASTIÃO"])

    texto_outorgado = ""
    for i, advogado in enumerate(advogados_selecionados):
        partes = [
            f"{advogado['nome']}",
            "brasileiro" if advogado["estado_civil"] == "solteiro" else "brasileiro, " + advogado["estado_civil"],
            advogado["profissao"],
            f"inscrito no CPF sob o n.º {advogado['cpf']}",
            f"RG n.º {advogado['rg']}, {advogado['orgao_emissor']}"
        ]

        if len(advogado["oab"]) == 1:
            partes.append(f"OAB/RO n.º {advogado['oab'][0]}")
        else:
            partes.append(f"OAB/PR n.º {advogado['oab'][0]}, e OAB/RO n.º {advogado['oab'][1]}")

        texto_outorgado += ", ".join(partes)

        if i < len(advogados_selecionados) - 1:
            texto_outorgado += " & "

    texto_outorgado += f", com endereço profissional situado na {ENDERECO_ADV}."

    pdf.set_x(37.5)
    pdf.multi_cell(0, 7, texto_outorgado)
    pdf.ln(5)

    # Poderes
    pdf.set_font("Times", 'B', 12)
    pdf.cell(0, 7, "PODERES GERAIS:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Times", size=12)

    poderes = "O outorgante nomeia os outorgados seus procuradores, concedendo-lhes os poderes inerentes da cláusula ad judicia et extra para o foro em geral, podendo promover quaisquer medidas judiciais ou administrativas, oferecer defesa, interpor recursos, ajuizar ações e conduzir os respectivos processos, solicitar, providenciar e ter acesso a documentos de qualquer natureza, sendo o presente instrumento de mandato oneroso e contratual, podendo substabelecer este a outrem, com ou sem reserva de poderes, a fim de praticar todos os demais atos necessários ao fiel desempenho deste mandato, além de reconhecer a procedência do pedido, transigir, desistir, renunciar ao direito sobre o qual se funda a ação, receber, dar quitação, firmar compromisso e assinar declaração de hipossuficiência econômica."

    pdf.set_x(37.5)
    pdf.multi_cell(0, 7, poderes)
    pdf.ln(10)

    # Data e assinatura
    data_atual = datetime.now().strftime("%d de %B de %Y").lower()
    meses = {
        "january": "janeiro", "february": "fevereiro", "march": "março",
        "april": "abril", "may": "maio", "june": "junho",
        "july": "julho", "august": "agosto", "september": "setembro",
        "october": "outubro", "november": "novembro", "december": "dezembro"
    }
    for eng, pt in meses.items():
        data_atual = data_atual.replace(eng, pt)

    pdf.set_font("Times", size=12)
    pdf.cell(0, 7, f"Machadinho D'Oeste, {data_atual}.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(15)

    # Linha para assinatura
    pdf.cell(0, 7, "___________________________", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.cell(0, 7, "OUTORGANTE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    # Salva o arquivo temporário
    nome_arquivo = f"Procuração_{dados_cliente['nome_completo'].replace(' ', '_')}.pdf"
    caminho_arquivo = os.path.join('static/temp', nome_arquivo)
    pdf.output(caminho_arquivo)

    return caminho_arquivo


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/gerar-procuracao', methods=['POST'])
def gerar_procuracao_route():
    try:
        data = request.json

        # Validação dos dados
        required_fields = ['nome_completo', 'profissao', 'cpf', 'endereco', 'estado_civil']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'O campo {field.replace("_", " ")} é obrigatório!'}), 400

        # Validação do CPF
        cpf_limpo = ''.join(filter(str.isdigit, data['cpf']))
        if len(cpf_limpo) != 11:
            return jsonify({'error': 'CPF deve conter 11 dígitos!'}), 400

        # Formata o CPF
        data['cpf'] = formatar_cpf(data['cpf'])

        # Padroniza os dados
        data['nome_completo'] = data['nome_completo'].upper()
        data['estado_civil'] = data['estado_civil'].lower()
        data['profissao'] = data['profissao'].lower()

        # Gera a procuração
        arquivo = gerar_procuracao(
            data,
            data.get('incluir_thayrone', True),
            data.get('incluir_sebastiao', False)
        )

        return jsonify({
            'success': True,
            'filename': os.path.basename(arquivo),
            'download_url': f'/download/{os.path.basename(arquivo)}'
        })

    except Exception as e:
        return jsonify({'error': f'Ocorreu um erro ao gerar a procuração: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_file(filename):
    return send_file(
        os.path.join('static/temp', filename),
        as_attachment=True,
        download_name=filename
    )


if __name__ == '__main__':
    os.makedirs('static/temp', exist_ok=True)
    app.run(debug=True)