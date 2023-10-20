from control import exec_base_value, img_retriv, exec_busca_prod, exec_config, exec_recommendation
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
    cd_prod, cd_filial = exec_busca_prod(cd_barra=request.json['cd_prod']), int(str(request.json['cd_filial'])[:-1])
    if cd_prod['boll'] is not True:
        response = {'boll': False, 'mensage': 'Lamento, produto não encontrado :('}
        return response
    result, etiquetas = exec_base_value(cd_prod=cd_prod['cd_prod'], cd_filial=cd_filial), []
    if result['boll'] is not True:
        response = {'boll': False, 'mensage': 'Lamento, produto não encontrado :('}
        return response
    ret = exec_recommendation(cd_prod=cd_prod['cd_prod'], cd_filial=cd_filial)
    img = img_retriv(cd_prod=cd_prod['cd_prod'])
    if result['flag_estoque'] == 1:
        estoque = True
    else:
        estoque = False
    if result['flag_oferta'] == 1:
        etiquetas.append({
            'tipo': 'rebaixa',
            'txtPromocional': 'Oferta',
            'PrecoProduto': result['valor_tabela'],
            'PrecoPromo': result['valor_final']
        })
    if result['flag_desc_acima'] == 1:
        etiquetas.append({
            'tipo': 'acimaDe',
            'txtPromocional': f"{result['perc_acima']}% a partir da {result['acima_unidade']} unidade",
            'PrecoProduto': result['valor_final'],
            'PrecoPromo': result['acima_valor'],
            'APLICA_UN': True
        })
    if result['flag_pague_leve'] == 1:
        etiquetas.append({"tipo": 'Leve Pague',
                          "txtPromocional": f"Leve {result['qtde_leve']} Pague {result['qtde_pague']}",
                          "PrecoProduto": result['valor_final'],
                          "PrecoPromo": result['valor_pague_leve'],
                          "APLICA_UN": True})
    if result['flag_kit'] == 1:
        if result['valor_produto_kit'] == 0.01:
            gratis = True
        else:
            gratis = False
        img_kit = img_retriv(cd_prod=result['cd_prod_kit'])
        etiquetas.append({
            "tipo": "kit",
            "PrecoProduto": result['valor_final'],
            "brinde": {
                "descricao": result['produto_leve_kit'],
                "imagemUrl": img_kit,
                "precoOriginalBrinde": result['valor_de_produto_kit'],
                "precoBrinde": result['valor_produto_kit'],
                "GRATIS": gratis
            }
        })

    if not etiquetas:
        etiquetas.append({
            'tipo': 'nenhum',
            'PrecoProduto': result['valor_final']
        })

    res = []
    if ret['boll'] is True:
        for i in ret['prods']:
            result, etiquetas = exec_base_value(cd_prod=i, cd_filial=cd_filial), []
            img = img_retriv(cd_prod=i)
            if result['flag_estoque'] == 1:
                estoque = True
            else:
                estoque = False
            if result['flag_oferta'] == 1:
                etiquetas.append({
                    'tipo': 'rebaixa',
                    'txtPromocional': 'Oferta',
                    'PrecoProduto': result['valor_tabela'],
                    'PrecoPromo': result['valor_final']
                })
            if result['flag_desc_acima'] == 1:
                etiquetas.append({
                    'tipo': 'acimaDe',
                    'txtPromocional': f"{result['perc_acima']}% a partir da {result['acima_unidade']} unidade",
                    'PrecoProduto': result['valor_final'],
                    'PrecoPromo': result['acima_valor'],
                    'APLICA_UN': True
                })
            if result['flag_pague_leve'] == 1:
                etiquetas.append({"tipo": 'Leve Pague',
                                  "txtPromocional": f"Leve {result['qtde_leve']} Pague {result['qtde_pague']}",
                                  "PrecoProduto": result['valor_final'],
                                  "PrecoPromo": result['valor_pague_leve'],
                                  "APLICA_UN": True})
            if result['flag_kit'] == 1:
                if result['valor_produto_kit'] == 0.01:
                    gratis = True
                else:
                    gratis = False
                img_kit = img_retriv(cd_prod=result['cd_prod_kit'])
                etiquetas.append({
                    "tipo": "kit",
                    "PrecoProduto": result['valor_final'],
                    "brinde": {
                        "descricao": result['produto_leve_kit'],
                        "imagemUrl": img_kit,
                        "precoOriginalBrinde": result['valor_de_produto_kit'],
                        "precoBrinde": result['valor_produto_kit'],
                        "GRATIS": gratis
                    }
                })
            if not etiquetas:
                etiquetas.append({
                    'tipo': 'nenhum',
                    'PrecoProduto': result['valor_final']
                })
            final = {
                'boll': True,
                'descricao': result['descricao'],
                'imagemUrl': img,
                'etiquetas': etiquetas,
                'estoque': estoque
            }
            res.append(final)
    final = {
        'boll': True,
        'descricao': result['descricao'],
        'imagemUrl': img,
        'descricaoCompleta': result['ds_e_commerce'],
        'etiquetas': etiquetas,
        'estoque': estoque,
        'recomendacao': res
    }
    return jsonify(final)


if __name__ == '__main__':
    num_cores = multiprocessing.cpu_count()
    print(f"Servidor executando com {num_cores} cores")
    serve(app, host='0.0.0.0', port=5000, threads=num_cores)
    # app.run(host='0.0.0.0', port=5000, debug=True)
