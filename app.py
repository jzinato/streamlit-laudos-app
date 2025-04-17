
import streamlit as st
import fitz  # PyMuPDF
from supabase import create_client, Client
from datetime import datetime
from docx import Document
from io import BytesIO

# Configurações Supabase
SUPABASE_URL = "https://dlbqbfoiywhoypsxyrfd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRsYnFiZm9peXdob3lwc3h5cmZkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ4NDg1MjAsImV4cCI6MjA2MDQyNDUyMH0.3xxn7FfpKhw7yp9Iow1Zd0K6IDhl5yLFJioQmd8QmM4"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def extrair_texto(pdf_file):
    texto = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            texto += page.get_text()
    return texto

def salvar_laudo(nome, cpf, data_nasc, texto):
    data_laudo = datetime.now().isoformat()
    supabase.table("laudos").insert({
        "nome": nome,
        "cpf": cpf,
        "data_nasc": data_nasc,
        "data_laudo": data_laudo,
        "conteudo": texto
    }).execute()

def gerar_relatorio(texto_extraido):
    doc = Document()
    doc.add_heading("Relatório Gerado a partir de Laudo PDF", 0)
    for linha in texto_extraido.splitlines():
        doc.add_paragraph(linha.strip())
    output = BytesIO()
    doc.save(output)
    return output.getvalue()

st.title("App de Laudos - Dr. João Batista Zinato")
with st.form("form_laudo"):
    nome = st.text_input("Nome do paciente")
    cpf = st.text_input("CPF")
    data_nasc = st.date_input("Data de nascimento")
    arquivo_pdf = st.file_uploader("Laudo em PDF", type="pdf")
    submitted = st.form_submit_button("Processar Laudo")

if submitted and arquivo_pdf:
    texto = extrair_texto(arquivo_pdf)
    salvar_laudo(nome, cpf, str(data_nasc), texto)
    st.success("Laudo processado e salvo com sucesso.")
    st.subheader("Texto extraído do PDF:")
    st.text_area("Conteúdo", texto, height=300)
    relatorio_docx = gerar_relatorio(texto)
    st.download_button("Download do Relatório Word", relatorio_docx, file_name="relatorio.docx")

st.divider()
st.subheader("🔍 Consultar Laudos Cadastrados")
laudos = supabase.table("laudos").select("*").order("data_laudo", desc=True).execute()
for entry in laudos.data:
    st.markdown(f"**{entry['nome']}** - {entry['data_laudo'][:10]}")
    with st.expander("Ver conteúdo"):
        st.write(entry['conteudo'])
