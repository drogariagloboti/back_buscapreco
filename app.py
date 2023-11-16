import os
import subprocess
from control import exec_base_value, img_retriv, exec_busca_prod, exec_config, exec_recommendation, exec_carousel, \
    exec_not_foun, exec_control_scan, exec_next_banner, exec_insert_banner
import threading
from waitress import serve
from flask import Flask, request, jsonify
from flask_cors import CORS
import mini_queue
from PIL import Image
import io

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
if not os.path.isdir(f'./banner'):
    os.mkdir(f"./banner")
if not os.path.isdir(f"./banner/micro"):
    os.mkdir(f"./banner/micro")

banner_path = os.getcwd()


@app.route('/config', methods=['POST'])
def config():
    cd_filial = int(str(request.json['cd_filial'])[:-1])
    ret = exec_config(cd_filial=cd_filial)
    return ret


@app.route('/', methods=['POST'])
def main():
    cd_bar = request.json['cd_prod']
    cd_prod = exec_busca_prod(cd_barra=cd_bar)
    cd_filial = int(str(request.json['cd_filial'])[:-1])
    exec_control_scan(cd_filial=cd_filial, cd_prod=cd_prod)
    if cd_prod['boll'] is not True:
        response = {'boll': False, 'mensage': 'Lamento, produto não encontrado :('}
        exec_not_foun({'ean': cd_bar, 'cd_filial': cd_filial})
        return response
    result, etiquetasp = exec_base_value(cd_prod=cd_prod['cd_prod'], cd_filial=cd_filial, cd_bar=cd_bar), None
    if result['boll'] is not True:
        response = {'boll': False, 'mensage': 'Lamento, produto não encontrado :('}
        return response
    ret = exec_recommendation(cd_prod=cd_prod['cd_prod'], cd_filial=cd_filial)
    imgp = img_retriv(cd_prod=cd_prod['cd_prod'])
    if result['flag_estoque'] == 1:
        estoquep = True
    else:
        estoquep = False
    if result['flag_oferta'] == 1:
        etiquetasp = [{
            'tipo': 'rebaixa',
            'txtPromocional': 'Oferta',
            'PrecoProdutoReais': result['valor_tabela'].split('.')[0],
            'PrecoProdutoCentavos': ',' + result['valor_tabela'].split('.')[1],
            'PrecoPromoReais': result['valor_final'].split('.')[0],
            'PrecoPromoCentavos': ',' + result['valor_final'].split('.')[1]
        }]
    if result['flag_desc_acima'] == 1:
        if result['acima_unidade'] == 1:
            etiquetasp = [{
                'tipo': 'acimaDe',
                'txtPromocional': f"{result['perc_acima']}% de desconto",
                'PrecoProdutoReais': result['valor_final'].split('.')[0],
                'PrecoProdutoCentavos': ',' + result['valor_final'].split('.')[1],
                'PrecoPromoReais': result['acima_valor'].split('.')[0],
                'PrecoPromoCentavos': ',' + result['acima_valor'].split('.')[1],
                'APLICA_UN': True
            }]
        else:
            etiquetasp = [{
                'tipo': 'acimaDe',
                'txtPromocional': f"{result['perc_acima']}% de desconto a partir da {result['acima_unidade']}° unidade",
                'PrecoProdutoReais': result['valor_final'].split('.')[0],
                'PrecoProdutoCentavos': ',' + result['valor_final'].split('.')[1],
                'PrecoPromoReais': result['acima_valor'].split('.')[0],
                'PrecoPromoCentavos': ',' + result['acima_valor'].split('.')[1],
                'APLICA_UN': True
            }]
    if result['flag_pague_leve'] == 1:
        etiquetasp = [{"tipo": 'Leve Pague',
                       "txtPromocional": f"Leve {result['qtde_leve']} Pague {result['qtde_pague']}",
                       "PrecoProdutoReais": result['valor_final'].split('.')[0],
                       "PrecoProdutoCentavos": ',' + result['valor_final'].split('.')[1],
                       "PrecoPromoReais": result['valor_pague_leve'].split('.')[0],
                       "PrecoPromoCentavos": ',' + result['valor_pague_leve'].split('.')[1],
                       "APLICA_UN": True}]
    # if result['flag_kit'] == 1:
    #    if result['valor_produto_kit'] == 0.01:
    #        gratis = True
    #    else:
    #        gratis = False
    #    img_kit = img_retriv(cd_prod=result['cd_prod_kit'])
    #    etiquetasp.append({
    #        "tipo": "kit",
    #        "PrecoProduto": result['valor_final'],
    #        "brinde": {
    #            "descricao": result['produto_leve_kit'],
    #            "imagemUrl": img_kit,
    #            "precoOriginalBrinde": result['valor_de_produto_kit'],
    #            "precoBrinde": result['valor_produto_kit'],
    #            "GRATIS": gratis
    #        }
    #    })
    if result['flag_pre_vencido'] == 1:
        etiquetasp = [{"tipo": 'Pre',
                       "txtPromocional": f"PRODUTO PRÓXIMO AO VENCIMENTO",
                       "PrecoProdutoReais": result['valor_final'].split('.')[0],
                       "PrecoProdutoCentavos": ',' + result['valor_final'].split('.')[1],
                       "PrecoPromoReais": result['pre_vencido'].split('.')[0],
                       "PrecoPromoCentavos": ',' + result['pre_vencido'].split('.')[1]}]

    if etiquetasp is None:
        etiquetasp = [{
            'tipo': 'nenhum',
            'PrecoProdutoReais': result['valor_final'].split('.')[0],
            'PrecoProdutoCentavos': ',' + result['valor_final'].split('.')[1],
            'PrecoPromoReais': result['valor_final'].split('.')[0],
            'PrecoPromoCentavos': ',' + result['valor_final'].split('.')[1]
        }]

    res = []
    if ret['boll'] is True:
        for i in ret['prods']:
            result_rec, etiquetas = exec_base_value(cd_prod=i, cd_filial=cd_filial, cd_bar=cd_bar), []
            img = img_retriv(cd_prod=i)
            if result_rec['flag_oferta'] == 1:
                etiquetas.append({
                    'tipo': 'rebaixa',
                    'txtPromocional': 'Oferta',
                })
            if result_rec['flag_desc_acima'] == 1:
                if int(result_rec['acima_unidade']) == 1:
                    etiquetas.append({
                        'tipo': 'acimaDe',
                        'txtPromocional': f"{result_rec['perc_acima']}% de desconto",
                        'APLICA_UN': True
                    })
                else:
                    etiquetas.append({
                        'tipo': 'acimaDe',
                        'txtPromocional': f"{result_rec['perc_acima']}% de desconto a partir da {result_rec['acima_unidade']}° unidade",
                        'APLICA_UN': True
                    })
            if result_rec['flag_pague_leve'] == 1:
                etiquetas.append({"tipo": 'Leve Pague',
                                  "txtPromocional": f"Leve {result_rec['qtde_leve']} Pague {result_rec['qtde_pague']}",
                                  "APLICA_UN": True})
            # if result_rec['flag_kit'] == 1:
            #    if result_rec['valor_produto_kit'] == 0.01:
            #        gratis = True
            #    else:
            #        gratis = False
            #    img_kit = img_retriv(cd_prod=result_rec['cd_prod_kit'])
            #    etiquetas.append({
            #        "tipo": "kit",
            #        "brinde": {
            #            "descricao": result_rec['produto_leve_kit'],
            #            "imagemUrl": img_kit,
            #            "GRATIS": gratis
            #        }
            #    })
            if not etiquetas:
                etiquetas.append({
                    'tipo': 'nenhum',
                })
            final = {
                'boll': True,
                'descricao': result_rec['descricao'],
                'imagemUrl': img,
                'etiquetas': etiquetas
            }
            res.append(final)
    if result['flag_pre_vencido'] == 1:
        est = result['estoque_pre']
    else:
        est = result['estoque']
    mini = None
    if ret['boll'] is False:
        mini = mini_queue.next()
    final = {
        'boll': True,
        'descricao': result['descricao'],
        'imagemUrl': imgp,
        'descricaoCompleta': result['ds_e_commerce'],
        'pbm': result['flag_pbm'],
        'popular': result['flag_popular'],
        'etiquetas': etiquetasp,
        'estoque': estoquep,
        'qt_est': est,
        'recomendacao': res,
        'mini': mini
    }
    return jsonify(final)


@app.route('/banner', methods=['POST'])
def banner():
    carousel = exec_carousel(int(str(request.json['cd_filial'])[:-1]))
    return jsonify(carousel)


def salvar_banner(imagem, path):
    imagem = Image.open(io.BytesIO(imagem))
    imagem.save(banner_path + path)



@app.route('/cadastro_banner', methods=['POST'])
def verificar_dimensoes():
    imagem, path = request.files['banner'].read(), request.files['banner'].filename
    imagem_mini, path_mini = request.files['mini'].read(), request.files['mini'].filename
    form = {
        'path': 'http://10.10.0.56:8855/' + path,
        'dt_ini': request.form['dt_ini'],
        'dt_fim': request.form['dt_fim'],
        'ativo': int(request.form['ativo']),
        'cd_filial': int(request.form['cd_filial'])
    }
    next_banner = exec_next_banner()
    form_mini = {
        'banner_id': next_banner,
        'path': 'http://10.10.0.56:8855/micro/' + path_mini,
        'ativo': 1
    }
    exec_insert_banner(form=form, form_mini=form_mini)
    salvar_banner(imagem, '\\banner\\'+path)
    salvar_banner(imagem_mini, '\\banner\\micro\\' + request.files['mini'].filename)
    return jsonify({"bool": True, "mensagem": "Imagem inserida com sucesso."})


#
def start_flask():
    if __name__ == '__main__':
        # num_cores = multiprocessing.cpu_count()
        # print(f"Servidor executando com {num_cores} cores")
        serve(app, host='0.0.0.0', port=8850)
        # app.run(host='0.0.0.0', port=5000, debug=True)


def start_img_server():
    diretorio_banner = os.getcwd() + '\\banner'  # Substitua pelo caminho real do diretório 'banner'
    os.chdir(diretorio_banner)
    comando = f"python -m http.server 8000"
    subprocess.run(comando, shell=True)


thread_flask = threading.Thread(target=start_flask)
thread_img_server = threading.Thread(target=start_img_server)
thread_img_server.start()
thread_flask.start()



