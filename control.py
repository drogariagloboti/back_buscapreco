from connect import sqlserver, postgressbd, postgressbd_local
from models import base_value, result, img, busca_prod, config, recommendation


def exec_busca_prod(cd_barra):
    conn = sqlserver()
    cursor = conn.cursor()
    cursor.execute(busca_prod(cd_barra=cd_barra))
    r = cursor.fetchone()
    if r is None:
        conn.commit()
        conn.close()
        return {'boll': False}
    else:
        conn.commit()
        conn.close()
        return {'boll': True, 'cd_prod': r[0]}


def exec_base_value(cd_prod, cd_filial):
    try:
        conn = sqlserver()
        cursor = conn.cursor()
        cursor.execute(base_value(cd_prod=cd_prod, cd_filial=cd_filial))
        cursor.execute(result())
        r = cursor.fetchone()
        if result is None:
            conn.commit()
            conn.close()
            return {'boll': False}
        else:
            conn.commit()
            conn.close()
            return {
                'boll': True,
                'cd_prod': r[0],
                'descricao': r[1],
                'filial': r[2],
                'ds_e_commerce': r[3],
                'valor_tabela': "{:.2f}".format(r[4]),
                'valor_tabloide': "{:.2f}".format(r[5]),
                'perc_desc': int(r[6]),
                'valor_final': "{:.2f}".format(r[7]),
                'acima_valor': "{:.2f}".format(r[8]),
                'acima_unidade': int(r[9]),
                'perc_acima': int(r[10]),
                'qtde_pague': r[11],
                'qtde_leve': r[12],
                'valor_pague_leve': "{:.2f}".format(r[13]),
                'compre_kit': "{:.2f}".format(r[14]),
                'leve_kit': "{:.2f}".format(r[15]),
                'cd_prod_kit': r[16],
                'produto_leve_kit': r[17],
                'valor_de_produto_kit': "{:.2f}".format(r[18]),
                'valor_produto_kit': "{:.2f}".format(r[19]),
                'flag_oferta': r[20],
                'flag_desc_acima': r[21],
                'flag_pague_leve': r[22],
                'flag_kit': r[23],
                'flag_estoque': r[24]
            }
    except:
        return {'boll': False}


def img_retriv(cd_prod):
    conn = postgressbd()
    cursor = conn.cursor()
    cursor.execute(img(cd_prod=cd_prod))
    r = cursor.fetchone()
    if not r:
        conn.commit()
        conn.close()
        return 'https://drogariaglobo.vteximg.com.br/arquivos/ids/1080886/Brinco-Perfurador-Lobeflex-Baby.jpg?v=638153479212870000'
    conn.commit()
    conn.close()
    return r[0]


def exec_config(cd_filial: int):
    conn = sqlserver()
    cursor = conn.cursor()
    cursor.execute(config(cd_filial=cd_filial))
    r = cursor.fetchone()
    if not r:
        conn.commit()
        conn.close()
        return {'boll': False, 'mensage': 'Codigo de configuração invalido'}
    else:
        conn.commit()
        conn.close()
        return {'boll': True, 'mensage': f'Busca preço filial {cd_filial}'}


def exec_recommendation(cd_prod: int, cd_filial: int):
    conn = postgressbd_local()
    cursor = conn.cursor()
    cursor.execute(recommendation(cd_prod=cd_prod, cd_filial=cd_filial))
    r, prods = cursor.fetchall(), []
    if not r:
        conn.commit()
        conn.close()
        return {'boll': False, 'mensage': 'nenhum patrocinio encontrado'}
    for i in r:
        prods.append(i[0])
    conn.commit()
    conn.close()
    return {'boll': True, 'prods': prods}
