# grid_nfe.py
from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
import os
import random
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

grid_nfe_bp = Blueprint('grid_nfe', __name__)

# Dados mock para simular o banco de dados
def gerar_dados_nfe():
    situacoes = ['Autorizado', 'Cancelado', 'Inutilizado', 'Denegado', 'Rejeitado', 'Em Processamento']
    ufs = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC']
    empresas = ['Empresa A Ltda', 'Empresa B SA', 'Comércio C ME', 'Indústria D EPP']

    nfe_list = []
    for i in range(1, 51):
        chave = f'352105075847180001355500100000{str(i).zfill(4)}0000{str(i).zfill(4)}'
        nfe_list.append({
            'id': i,
            'selecionado': False,
            'tipo_emissao': random.choice(['Normal', 'Contingência']),
            'manifestacao': random.choice(['Confirmada', 'Ciência', 'Desconhecida', 'Não Realizada', None]),
            'auditor': random.choice(['Crítica', 'Sugestão', 'Sem Ocorrências', 'Não Auditável']),
            'serie': str(random.randint(1, 5)),
            'numero': str(1000 + i),
            'chave_acesso': chave,
            'data_emissao': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%d/%m/%Y'),
            'data_processamento': (datetime.now() - timedelta(days=random.randint(0, 2))).strftime('%d/%m/%Y %H:%M'),
            'situacao': random.choice(situacoes),
            'motivo': 'Uso autorizado' if random.random() > 0.2 else 'Rejeitado: Erro no cadastro',
            'emitente': random.choice(empresas),
            'uf': random.choice(ufs),
            'destinatario': random.choice(empresas),
            'valor': f'R$ {random.uniform(100, 10000):.2f}',
            'cnpj_transportador': f'{random.randint(10, 99)}.{random.randint(100, 999)}.{random.randint(100, 999)}/0001-{random.randint(10, 99)}',
            'transportador': random.choice(['Transportadora X', 'Logística Y', 'Fretes Z']),
            'icms': f'R$ {random.uniform(10, 1000):.2f}',
            'descontos': f'R$ {random.uniform(0, 500):.2f}',
            'ipi': f'R$ {random.uniform(0, 300):.2f}',
            'pis_cofins': f'R$ {random.uniform(5, 200):.2f}'
        })

    return nfe_list

@grid_nfe_bp.route('/grid')
@login_required
def grid_nfe():
    dados_nfe = gerar_dados_nfe()
    return render_template('grid_nfe.html', nfe_list=dados_nfe, name=current_user.name)

@grid_nfe_bp.route('/api/filtrar', methods=['POST'])
@login_required
def filtrar_nfe():
    filtros = request.json
    dados_nfe = gerar_dados_nfe()

    # Aplicar filtros (simplificado)
    if filtros.get('situacao') and filtros['situacao'] != 'Todos':
        dados_nfe = [nfe for nfe in dados_nfe if nfe['situacao'] == filtros['situacao']]

    if filtros.get('data_inicio'):
        # Implementar lógica de filtro por data
        pass

    return jsonify(dados_nfe)

@grid_nfe_bp.route('/api/download', methods=['POST'])
@login_required
def download_xml():
    dados = request.json
    nfe_ids = dados.get('ids', [])

    # Simular geração de arquivos XML
    xml_files = []
    for nfe_id in nfe_ids:
        filename = f"nfe_{nfe_id}.xml"
        filepath = os.path.join('xml_files', filename)

        # Criar arquivo XML mock se não existir
        if not os.path.exists(filepath):
            criar_xml_mock(filepath, nfe_id)

        xml_files.append({
            'id': nfe_id,
            'filename': filename,
            'chave_acesso': f'352105075847180001355500100000{str(nfe_id).zfill(4)}0000{str(nfe_id).zfill(4)}'
        })

    return jsonify({
        'success': True,
        'files': xml_files,
        'message': f'{len(xml_files)} arquivo(s) preparado(s) para download'
    })

@grid_nfe_bp.route('/download/<filename>')
@login_required
def download_xml_file(filename):
    filepath = os.path.join('xml_files', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return "Arquivo não encontrado", 404

@grid_nfe_bp.route('/api/acoes-lote', methods=['POST'])
@login_required
def acoes_lote():
    dados = request.json
    acao = dados.get('acao')
    nfe_ids = dados.get('ids', [])

    if acao == 'download':
        return download_xml()
    elif acao == 'exportar_excel':
        return jsonify({'success': True, 'message': 'Exportação para Excel iniciada'})
    elif acao == 'enviar_email':
        return jsonify({'success': True, 'message': f'{len(nfe_ids)} NF-e(s) enviada(s) por email'})
    elif acao == 'enviar_erp':
        return jsonify({'success': True, 'message': f'{len(nfe_ids)} NF-e(s) enviada(s) ao ERP'})

    return jsonify({'success': False, 'message': 'Ação não implementada'})

def criar_xml_mock(filepath, nfe_id):
    """Cria um arquivo XML mock para simulação"""
    root = ET.Element('nfeProc', xmlns="http://www.portalfiscal.inf.br/nfe")

    # Adicionar elementos básicos do XML da NF-e
    infNFe = ET.SubElement(root, 'infNFe')
    ET.SubElement(infNFe, 'Id').text = f'NFe{nfe_id}'
    ET.SubElement(infNFe, 'cUF').text = '35'
    ET.SubElement(infNFe, 'cNF').text = str(nfe_id)
    ET.SubElement(infNFe, 'natOp').text = 'Venda de mercadoria'
    ET.SubElement(infNFe, 'mod').text = '55'
    ET.SubElement(infNFe, 'serie').text = '1'
    ET.SubElement(infNFe, 'nNF').text = str(nfe_id)
    ET.SubElement(infNFe, 'dhEmi').text = datetime.now().isoformat()

    # Emitente
    emit = ET.SubElement(infNFe, 'emit')
    ET.SubElement(emit, 'CNPJ').text = '07584718000135'
    ET.SubElement(emit, 'xNome').text = 'Empresa Mock Ltda'

    # Destinatário
    dest = ET.SubElement(infNFe, 'dest')
    ET.SubElement(dest, 'CNPJ').text = '12345678000190'
    ET.SubElement(dest, 'xNome').text = 'Cliente Exemplo SA'

    # Produtos
    det = ET.SubElement(infNFe, 'det')
    prod = ET.SubElement(det, 'prod')
    ET.SubElement(prod, 'cProd').text = 'PROD001'
    ET.SubElement(prod, 'xProd').text = 'Produto de Exemplo'
    ET.SubElement(prod, 'qCom').text = '10.0000'
    ET.SubElement(prod, 'vUnCom').text = '150.00'
    ET.SubElement(prod, 'vProd').text = '1500.00'

    # Total
    total = ET.SubElement(infNFe, 'total')
    icmsTot = ET.SubElement(total, 'ICMSTot')
    ET.SubElement(icmsTot, 'vBC').text = '1500.00'
    ET.SubElement(icmsTot, 'vICMS').text = '270.00'
    ET.SubElement(icmsTot, 'vProd').text = '1500.00'
    ET.SubElement(icmsTot, 'vNF').text = '1500.00'

    # Criar árvore XML e salvar
    tree = ET.ElementTree(root)
    tree.write(filepath, encoding='utf-8', xml_declaration=True)

# Inicialização - criar diretório se não existir
def init_grid_nfe():
    os.makedirs('xml_files', exist_ok=True)

# Chamar inicialização quando o módulo for importado
init_grid_nfe()
