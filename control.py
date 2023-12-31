from connect import sqlserver, postgressbd, postgressbd_local
from models import base_value, result, img, busca_prod, config, recommendation, carousel, parametros, minibanner, \
    not_found, select_filial, insert_scan, update_scan, next_banner, insert_banner, insert_banner_mini


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


def exec_base_value(cd_prod, cd_filial, cd_bar):
    try:
        conn = sqlserver()
        cursor = conn.cursor()
        cursor.execute(base_value(cd_prod=cd_prod, cd_filial=cd_filial, cd_bar=cd_bar))
        cursor.execute(result())
        r = cursor.fetchone()
        if result is None:
            conn.commit()
            conn.close()
            return {'boll': False}
        else:
            if r[3] is not None:
                text = r[3]
            else:
                text = str(r[1]).title()
            conn.commit()
            conn.close()
            return {
                'boll': True,
                'cd_prod': r[0],
                'descricao': r[1],
                'filial': r[2],
                'ds_e_commerce': text,
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
                'pre_vencido': "{:.2f}".format(r[20]),
                'estoque_pre': int(r[21]),
                'flag_pbm': r[22],
                'flag_popular': r[23],
                'flag_oferta': r[24],
                'flag_desc_acima': r[25],
                'flag_pague_leve': r[26],
                'flag_kit': r[27],
                'flag_pre_vencido': r[28],
                'flag_estoque': r[29],
                'estoque': int(r[30])
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
        pgconn = postgressbd_local()
        pgcursor = pgconn.cursor()
        pgcursor.execute(parametros())
        par = pgcursor.fetchone()
        ret = {'boll': True,
               'mensage': f'Busca preço filial {cd_filial}',
               'filial': cd_filial,
               'banner_time': par[1],
               'product_time': par[2],
               'notfound_time': par[3]}
        pgconn.commit()
        pgconn.close()
        return ret


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


def exec_carousel(cd_filial):  # page):
    conn = postgressbd_local()
    cursor = conn.cursor()
    cursor.execute(carousel(cd_filial))
    carouse = cursor.fetchall()
    ret = []
    for i in carouse:  # [index:end_index]:
        ret.append({
            'id': i[0],
            'banner': i[1]
        })
    return {'banner': ret}  # , 'maxpage': maxpage}


def exec_minibanner():
    conn = postgressbd_local()
    cursor = conn.cursor()
    cursor.execute(minibanner())
    mini = cursor.fetchall()
    ret_mini = []
    if not mini:
        conn.commit()
        conn.close()
        return []
    for i in mini:
        ret_mini.append(i[2])
    conn.commit()
    conn.close()
    return ret_mini


def exec_not_foun(prod_not_found):
    conn = postgressbd_local()
    cursor = conn.cursor()
    cursor.execute(not_found(prod_not_found=prod_not_found))
    conn.commit()
    conn.close()


def exec_control_scan(cd_filial, cd_prod):
    conn = postgressbd_local()
    cursor = conn.cursor()
    # cursor.execute(select_filial(cd_filial=cd_filial))
    # data_exist = cursor.fetchone()
    # if not data_exist:
    if cd_prod['boll'] is not True:
        cursor.execute(insert_scan(cd_filial=cd_filial, cd_prod=0))
    else:
        cursor.execute(insert_scan(cd_filial=cd_filial, cd_prod=cd_prod['cd_prod']))
    # else:
    #    cursor.execute(update_scan(cd_filial=cd_filial,count=int(data_exist[2])))
    conn.commit()
    conn.close()


def exec_next_banner():
    conn = postgressbd_local()
    cursor = conn.cursor()
    cursor.execute(next_banner())
    ret = cursor.fetchone()
    conn.commit()
    conn.close()
    return int(ret[0])


def exec_insert_banner(form, form_mini):
    conn = postgressbd_local()
    cursor = conn.cursor()
    cursor.execute(insert_banner(form=form))
    cursor.execute(insert_banner_mini(form_mini=form_mini))
    conn.commit()
    conn.close()
