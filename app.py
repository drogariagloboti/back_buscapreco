from control import exec_base_value, img_retriv, exec_busca_prod, exec_config, exec_recommendation, exec_carousel
import multiprocessing
from waitress import serve
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


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
    if cd_prod['boll'] is not True:
        response = {'boll': False, 'mensage': 'Lamento, produto não encontrado :('}
        return response
    result, etiquetasp = exec_base_value(cd_prod=cd_prod['cd_prod'], cd_filial=cd_filial, cd_bar=cd_bar), []
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
        etiquetasp.append({
            'tipo': 'rebaixa',
            'txtPromocional': 'Oferta',
            'PrecoProdutoReais': result['valor_tabela'].split('.')[0],
            'PrecoProdutoCentavos': ','+result['valor_tabela'].split('.')[1],
            'PrecoPromoReais': result['valor_final'].split('.')[0],
            'PrecoPromoCentavos': ','+result['valor_final'].split('.')[1]
        })
    if result['flag_desc_acima'] == 1:
        if result['acima_unidade'] == 1:
            etiquetasp.append({
                'tipo': 'acimaDe',
                'txtPromocional': f"{result['perc_acima']}% OFF",
                'PrecoProdutoReais': result['valor_final'].split('.')[0],
                'PrecoProdutoCentavos': ','+result['valor_final'].split('.')[1],
                'PrecoPromoReais': result['acima_valor'].split('.')[0],
                'PrecoPromoCentavos': ','+result['acima_valor'].split('.')[1],
                'APLICA_UN': True
            })
        else:
            etiquetasp.append({
                'tipo': 'acimaDe',
                'txtPromocional': f"{result['perc_acima']}% OFF a partir da {result['acima_unidade']}° unidade",
                'PrecoProdutoReais': result['valor_final'].split('.')[0],
                'PrecoProdutoCentavos': ','+result['valor_final'].split('.')[1],
                'PrecoPromoReais': result['acima_valor'].split('.')[0],
                'PrecoPromoCentavos': ','+result['acima_valor'].split('.')[1],
                'APLICA_UN': True
            })
    if result['flag_pague_leve'] == 1:
        etiquetasp.append({"tipo": 'Leve Pague',
                           "txtPromocional": f"Leve {result['qtde_leve']} Pague {result['qtde_pague']}",
                           "PrecoProdutoReais": result['valor_final'].split('.')[0],
                           "PrecoProdutoCentavos": ','+result['valor_final'].split('.')[1],
                           "PrecoPromoReais": result['valor_pague_leve'].split('.')[0],
                           "PrecoPromoCentavos": ','+result['valor_pague_leve'].split('.')[1],
                           "APLICA_UN": True})
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
        etiquetasp.append({"tipo": 'Pre',
                           "txtPromocional": f"PRODUTO PRÓXIMO AO VENCIMENTO",
                           "PrecoProdutoReais": result['valor_final'].split('.')[0],
                           "PrecoProdutoCentavos": ','+result['valor_final'].split('.')[1],
                           "PrecoPromoReais": result['pre_vencido'].split('.')[0],
                           "PrecoPromoCentavos": ','+result['pre_vencido'].split('.')[1]})


    if not etiquetasp:
        etiquetasp.append({
            'tipo': 'nenhum',
            'PrecoProdutoReais': result['valor_final'].split('.')[0],
            'PrecoProdutoCentavos': ','+result['valor_final'].split('.')[1],
            'PrecoPromoReais': result['valor_final'].split('.')[0],
            'PrecoPromoCentavos': ','+result['valor_final'].split('.')[1]
        })

    res = []
    if ret['boll'] is True:
        for i in ret['prods']:
            result_rec, etiquetas = exec_base_value(cd_prod=i, cd_filial=cd_filial,cd_bar=cd_bar), []
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
                        'txtPromocional': f"{result_rec['perc_acima']}% OFF",
                        'APLICA_UN': True
                    })
                else:
                    etiquetas.append({
                        'tipo': 'acimaDe',
                        'txtPromocional': f"{result_rec['perc_acima']}% OFF a partir da {result_rec['acima_unidade']} unidade",
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
    final = {
        'boll': True,
        'descricao': result['descricao'],
        'imagemUrl': imgp,
        'descricaoCompleta': result['ds_e_commerce'],
        'etiquetas': etiquetasp,
        'estoque': estoquep,
        'qt_est': est,
        'recomendacao': res
    }
    return jsonify(final)


@app.route('/banner', methods=['GET'])
def banner():
    # query_params = urllib.parse.parse_qs(request.query_string.decode())
    # page = query_params.get('page', [''])[0]
    carousel = exec_carousel()
    return jsonify(carousel)


if __name__ == '__main__':
    num_cores = multiprocessing.cpu_count()
    print(f"Servidor executando com {num_cores} cores")
    serve(app, host='0.0.0.0', port=5000, threads=num_cores)
    # app.run(host='0.0.0.0', port=5000, debug=True)
