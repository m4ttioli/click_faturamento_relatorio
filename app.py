import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from relatorio.pdf_generator import gerar_pdf_relatorio

st.set_page_config(page_title="Relatório de Faturamento", layout="wide")

st.title("📊 Relatório de Faturamento")
st.markdown("Faça upload de uma planilha Excel para gerar o relatório em PDF.")

arquivo = st.file_uploader("Upload do Excel", type=["xls", "xlsx"])

if arquivo:
    try:
        df = pd.read_excel(arquivo)

        st.subheader("📄 Visualização da Planilha")
        st.dataframe(df, use_container_width=True)    

        min_nota = df["DAT_EMISSAO"].min()
        max_nota = df["DAT_EMISSAO"].max()
        st.markdown("### 🔢 Período analisado")
        col1, col2, = st.columns(2)
        col1.metric("Data Inicial", min_nota)
        col2.metric("Data Inicial", max_nota)

        # Conversão de datas
        df["DAT_EMISSAO"] = pd.to_datetime(df["DAT_EMISSAO"], format="%d/%m/%Y")

        # KPIs
        total_notas = df["NUM_NOTA"].nunique()
        total_valor_itens = df["ITEM_VAL_TOTAL"].sum()
        total_desconto = df["ITEM_VAL_DESCTO"].sum()
        total_valor_total = total_valor_itens - total_desconto # df["NOTA_VAL_TOTAL"].sum()

        st.markdown("### 🔢 Indicadores")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Qtd. Total de Notas", total_notas)
        col2.metric("Total em Valor Bruto", f"R$ {total_valor_itens:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        col3.metric("Total em Descontos", f"R$ {total_desconto:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        col4.metric("Total em Valor Líquido", f"R$ {total_valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        # col5.metric("Valor ICMS", f"R$ {total_icms:,.2f}")

        if st.button("📄 Gerar Relatório PDF"):
            name_file = 'FATUR_001_' + datetime.now().strftime('%Y%m%d_%H%M')
            gerar_pdf_relatorio(df, name_file)   

        st.markdown("### 📈 Gráficos de Análise")

        # Valor total por cliente
        valor_por_cliente = df.groupby("DES_CLIENTE")["NOTA_VAL_TOTAL"].sum().sort_values(ascending=False).reset_index()
        fig1 = px.bar(valor_por_cliente, x="NOTA_VAL_TOTAL", y="DES_CLIENTE", orientation="h",
                    title="Valor Total por Cliente", labels={"NOTA_VAL_TOTAL": "Valor Total", "DES_CLIENTE": "Cliente"})
        st.plotly_chart(fig1, use_container_width=True)

        # Valor por CFOP
        valor_por_cfop = df.groupby("ITEM_COD_CFOP")["ITEM_VAL_TOTAL"].sum().reset_index()
        fig2 = px.pie(valor_por_cfop, values="ITEM_VAL_TOTAL", names="ITEM_COD_CFOP",
                    title="Distribuição do Valor Total por CFOP")
        st.plotly_chart(fig2, use_container_width=True)

        # Quantidade de produto por descrição
        qtd_por_produto = df.groupby("DES_PRODUTO")["QTD_PRODUTO"].sum().sort_values(ascending=False).head(20).reset_index()
        fig3 = px.bar(qtd_por_produto, x="QTD_PRODUTO", y="DES_PRODUTO", orientation="h",
                    title="Top 20 Produtos por Quantidade", labels={"QTD_PRODUTO": "Quantidade", "DES_PRODUTO": "Produto"})
        st.plotly_chart(fig3, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao ler a planilha: {e}")
