import os
from pathlib import Path
import streamlit as st
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import datetime


class PDF(FPDF):

    global title 
    title = 'Relatório de Faturamento - Diário'
    
    def header(self):
        # Logo
        logo = os.path.abspath(f'./static/logo_click.png')
        self.image(logo, 10, 8, 25)
        
        # Data-Hora
        self.set_font('helvetica', '', 8)
        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.set_xy(-60, 10)
        self.cell(50, 10, now, align='R')
        
        # Pagenum
        page = f'Página {self.page_no()}'
        self.set_xy(-60, 14)
        self.cell(50, 10, page, align='R')

        # title
        self.set_font('helvetica', 'B', 20)
        self.set_y(15)
        self.cell(0, 10, title, border=False, 
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(10)

    def nota_section(self, nota, df_nota):
        row = df_nota.iloc[0]
        
        val_item = row.NOTA_VAL_ITENS
        val_item = f'R$ {val_item:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

        val_descto = row.NOTA_VAL_DESCTO
        val_descto = f'R$ {val_descto:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

        val_total = row.NOTA_VAL_TOTAL
        val_total = f'R$ {val_total:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

        self.ln(2)
        self.set_font("helvetica", "", 8) # "B",
        self.cell(0, 4, f'Nota: {row.NUM_NOTA} | Série: {row.DES_SERIE} | Emissão: {row.DAT_EMISSAO.strftime("%d/%m/%Y")}', 
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 4, f'Cliente: {row.COD_CLIENTE} - {row.DES_CLIENTE}', 
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.cell(0, 4, f'Valor Itens: {val_item} | Desconto: {val_descto} | Total: {val_total}', 
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(2)

        self.set_font("helvetica", "B", 8)
        self.cell(10, 6, "Seq", border=1, align='C')
        self.cell(20, 6, "Cód.", border=1)
        self.cell(80, 6, "Produto", border=1)
        self.cell(10, 6, "UN", border=1, align='C')
        self.cell(20, 6, "Val. Unit.", border=1, align='R')
        self.cell(15, 6, "Qtd.", border=1, align='R')
        self.cell(20, 6, "Total", border=1, align='R')
        self.cell(20, 6, "Val. Descto.", border=1, align='R')
        self.ln()

        self.set_font("helvetica", "", 8)
        for _, item in df_nota.iterrows():
            x_start = self.get_x()
            y_start = self.get_y()
            descricao = str(item.DES_PRODUTO)
            width_descricao = 80
            text_width = self.get_string_width(descricao)
            if text_width > width_descricao:
                linhas = text_width / width_descricao
                linhas = int(linhas) + 1 if linhas > int(linhas) else int(linhas)
                desc_height = linhas * 5
            else:
                desc_height = 8
            row_height = max(desc_height, 8)
            if self.get_y() + row_height + 5 > self.h - self.b_margin:
                self.add_page()
            self.set_xy(x_start + 30, y_start)
            if text_width > width_descricao:
                self.multi_cell(width_descricao, 5, descricao, border=1)
                desc_height = self.get_y() - y_start
            else:
                self.cell(width_descricao, desc_height, descricao, border=1)
            max_height = max(desc_height, 8)
            self.set_xy(x_start, y_start)
            self.cell(10, max_height, str(item.NUM_SEQ), border=1, align='C')
            self.cell(20, max_height, str(item.COD_PRODUTO), border=1)
            self.set_xy(x_start + 30 + width_descricao, y_start)
            self.cell(10, max_height, str(item.COD_UNIDADE_FATURA), border=1, align='C')            
            self.cell(20, max_height, f"{val_item}", border=1, align='R')
            self.cell(15, max_height, f"{item.QTD_PRODUTO}", border=1, align='R')
            self.cell(20, max_height, f"{val_total}", border=1, align='R')
            self.cell(20, max_height, f"{val_descto}", border=1, align='R')            
            self.ln(max_height)
        self.ln(5)

    def summary_section(self, df):
        self.add_page()
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, "Totalizadores do Relatório", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(10)

        # Calculate totals
        total_notas = df['NUM_NOTA'].nunique()
        df_first_rows = df.groupby('NUM_NOTA').first()
        total_itens = df_first_rows['NOTA_VAL_ITENS'].sum()
        total_itens = f'R$ {total_itens:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

        total_desconto = df_first_rows['NOTA_VAL_DESCTO'].sum()
        total_desconto = f'R$ {total_desconto:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

        total_geral = df_first_rows['NOTA_VAL_TOTAL'].sum()
        total_geral = f'R$ {total_geral:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

        title_w = self.get_string_width(title) + 6
        doc_w = self.w
        center_set = ((doc_w - title_w) / 3)

        # Render summary table
        self.set_font("helvetica", "B", 10)
        self.set_x(center_set)
        self.cell(60, 8, "Descrição", border=1)
        self.cell(60, 8, "Valor", border=1, align='R')
        self.ln()

        self.set_font("helvetica", "", 10)
        self.set_x(center_set)
        self.cell(60, 8, "Quantidade Total (Notas)", border=1)
        self.cell(60, 8, f"{total_notas}", border=1, align='R')
        self.ln()
        self.set_x(center_set)
        self.cell(60, 8, "Valor Itens Total", border=1)
        self.cell(60, 8, f"{total_itens}", border=1, align='R')
        self.ln()
        self.set_x(center_set)
        self.cell(60, 8, "Valor Desconto Total", border=1)
        self.cell(60, 8, f"{total_desconto}", border=1, align='R')
        self.ln()
        self.set_x(center_set)
        self.cell(60, 8, "Valor Líquido Total", border=1)
        self.cell(60, 8, f"{total_geral}", border=1, align='R')
        self.ln()


def should_add_page(pdf, group, line_height=8):
    altura_fixa = 37  # Header (24mm) + table header (6mm) + spacing (7mm)
    altura_itens = 0
    largura_desc = 70
    for _, item in group.iterrows():
        texto = str(item.DES_PRODUTO)
        text_width = pdf.get_string_width(texto)
        if text_width > largura_desc:
            linhas = text_width / largura_desc
            linhas = int(linhas) + 1 if linhas > int(linhas) else int(linhas)
            altura = linhas * 5
        else:
            altura = line_height
        altura_itens += max(altura, line_height)
    altura_total = altura_fixa + altura_itens + 5  # Buffer
    espaco_restante = pdf.h - pdf.get_y() - pdf.b_margin
    return altura_total > espaco_restante


def gerar_pdf_relatorio(df, nome_arquivo):
    os.makedirs('./storage', exist_ok=True)
    caminho_pdf = Path(f"./storage/{nome_arquivo}.pdf")

    # Gerar PDF
    pdf = PDF("P", "mm", "Letter")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    for nota, group in df.groupby("NUM_NOTA"):
        if should_add_page(pdf, group):
            pdf.add_page()
        pdf.nota_section(nota, group)

    # Add summary section
    pdf.summary_section(df)  


    pdf.output(str(caminho_pdf))
    st.success("✅ PDF gerado com sucesso!")

    with open(caminho_pdf, "rb") as f:
        st.download_button(
            label="📥 Baixar PDF",
            data=f,
            file_name=caminho_pdf.name,
            mime="application/pdf"
        )
