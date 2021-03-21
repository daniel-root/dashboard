import pandas as pd
import os
import requests
from datetime import date


class Tratamento:
    def __init__(self, endereco):
        self.endereco = "output/{}".format(endereco)
        self.dados = pd.read_csv(self.endereco, sep=';')

    def mostrar(self):
        print(self.dados.head(3))

    def renomear(self):
        titulo = ['ANO', 'MES', 'COD_NCM', 'COD_UNIDADE', 'COD_PAIS', 'SG_UF',
                  'COD_VIA', 'COD_URF', 'VL_QUANTIDADE', 'VL_PESO_KG', 'VL_FOB']
        self.dados.columns = titulo

    def zero_a_esquerda(self):
        self.dados['COD_NCM'] = self.dados.COD_NCM.map("{:08}".format)
        self.dados['COD_URF'] = self.dados.COD_URF.map("{:07}".format)
        #self.dados['COD_SH4'] = self.dados.COD_SH4.map("{:04}".format)
        self.dados['COD_PAIS'] = self.dados.COD_PAIS.map("{:03}".format)

    def criar_coluna(self, tipo):
        if tipo[0] == 'I':
            self.dados['MOVIMENTACAO'] = "importação"
        else:
            self.dados['MOVIMENTACAO'] = "exportação"


def baixar_csv(url, endereco):
    resposta = requests.get(url, verify=False)
    if resposta.status_code == requests.codes.OK:
        with open(endereco, 'wb') as novo_arquivo:
            novo_arquivo.write(resposta.content)
        print("Download finalizado. Salvo em: {}".format(endereco))
    else:
        resposta.raise_for_status()


def baixar():
    BASE_URL = 'https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/{}.csv'
    OUTPUT_DIR = 'output'
    data_atual = date.today()
    ano_atual = data_atual.strftime('%Y')
    ate_ano = int(ano_atual)-3
    for i in range(int(ate_ano), int(ano_atual)):
        nome_arquivo = os.path.join(OUTPUT_DIR, 'IMP_{}.csv'.format(i))
        baixar_csv(BASE_URL.format('IMP_' + str(i)), nome_arquivo)

    for i in range(int(ate_ano), int(ano_atual)):
        nome_arquivo = os.path.join(OUTPUT_DIR, 'EXP_{}.csv'.format(i))
        baixar_csv(BASE_URL.format('EXP_' + str(i)), nome_arquivo)


if __name__ == "__main__":
    baixar()

    data_atual = date.today()
    ano_atual = data_atual.strftime('%Y')
    ate_ano = int(ano_atual)-3
    geral = pd.DataFrame({'ANO': [], 'MES': [], 'ANO': [], 'COD_NCM': [], 'COD_UNIDADE': [], 'COD_PAIS': [], 'SG_UF': [],
                          'COD_VIA': [], 'COD_URF': [], 'VL_QUANTIDADE': [], 'VL_PESO_KG': [], 'VL_FOB': [], 'MOVIMENTACAO': []})

    for i in range(int(ate_ano), int(ano_atual)):
        nome_imp = 'IMP_{}.csv'.format(i)
        tratamento_imp = Tratamento(nome_imp)
        tratamento_imp.renomear()
        tratamento_imp.zero_a_esquerda()
        tratamento_imp.criar_coluna(nome_imp)
        # tratamento_imp.mostrar()
        nome_exp = 'EXP_{}.csv'.format(i)
        tratamento_exp = Tratamento(nome_exp)
        tratamento_exp.renomear()
        tratamento_exp.zero_a_esquerda()
        tratamento_exp.criar_coluna(nome_exp)
        # tratamento_exp.mostrar()
        atual = pd.concat([tratamento_imp.dados, tratamento_exp.dados])
        geral = pd.concat([atual, geral])
    geral.to_csv("f_comex.csv", index=False)
