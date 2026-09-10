import json
import html
import math
import time
import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz

@st.cache_data
def carregar_traducoes(idioma):
    with open(f"locales/{idioma}.json", "r", encoding="utf-8") as f:
        return json.load(f)

def traduzir(chave, idioma):
    traducoes = carregar_traducoes(idioma)
    # Percorre chaves hierárquicas, por exemplo: "app.titulo".
    partes = chave.split(".")
    valor = traducoes
    for parte in partes:
        if isinstance(valor, dict) and parte in valor:
            valor = valor[parte]
        else:
            return chave
    return valor

def carregar_css(caminho_ficheiro):
    with open(caminho_ficheiro, "r", encoding="utf-8") as f:
        # Injeta o conteúdo do ficheiro CSS na interface do Streamlit.
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Evita reler e tratar o dataset em cada reexecução do Streamlit.
@st.cache_data
def carregar_dados():
    try:
        df_filmes = pd.read_csv("top_1000_imdb_movies.csv")
    except FileNotFoundError:
        return None
    df_filmes.drop(columns=["Unnamed: 0"], errors="ignore", inplace=True)
    df_filmes.drop_duplicates(inplace=True)
    df_filmes["Movie Name"] = df_filmes["Movie Name"].str.strip()
    df_filmes["Description"] = df_filmes["Description"].str.strip()
    # Extrai a primeira sequência de quatro dígitos do ano de lançamento.
    df_filmes["Year of Release"] = df_filmes["Year of Release"].astype(str).str.extract(r"(\d{4})")[0]
    df_filmes["Year of Release"] = pd.to_numeric(df_filmes["Year of Release"], errors="coerce")
    df_filmes.reset_index(drop=True, inplace=True)
    return df_filmes

@st.cache_data
def carregar_equivalencias():
    with open("locales/equivalencias_pt.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Constrói o formato padronizado utilizado para representar cada filme na aplicação.
def criar_filme(linha, score):
    return {
        "titulo": linha["Movie Name"],
        "score": score,
        "ano": linha["Year of Release"],
        "classificacao": linha["Movie Rating"],
        "duracao": linha["Watch Time"],
        "descricao": str(linha["Description"]) if pd.notna(linha["Description"]) else ""
    }

def obter_catalogo_filmes(df_filmes):
    # Cria a lista completa de filmes quando não existe uma pesquisa ativa.
    lista = []
    for _, linha in df_filmes.iterrows():
        lista.append(criar_filme(linha, 100.0))
    return lista

def limpar_artigos_pt(termo):
    t = termo.strip().lower()
    for art in ["o ", "a ", "os ", "as ", "um ", "uma "]:
        if t.startswith(art):
            return t[len(art):].strip()
    return t

# Remove artigos iniciais em inglês para reduzir correspondências indevidas na pesquisa fuzzy.
def limpar_artigos_iniciais(termo):
    t = termo.strip().lower()
    for art in ["the ", "a ", "an "]:
        if t.startswith(art):
            return t[len(art):].strip()
    return t

def obter_tokens_titulo(titulo):
    return [palavra.strip(":,.-_!?'\"()[]{}") for palavra in str(titulo).lower().split() if palavra]

def resolver_equivalencias(termo_pesquisa, limite_similaridade=80):
    # Resolve todas as equivalências encontradas, mantendo apenas a maior pontuação por título equivalente.
    try:
        equivalencias = carregar_equivalencias()
        termo_limpo = termo_pesquisa.strip().lower()
        
        if termo_limpo in equivalencias:
            return [(equivalencias[termo_limpo], 100.0)]
        
        termo_fuzzy_pt = limpar_artigos_pt(termo_limpo)
        if termo_fuzzy_pt in equivalencias:
            return [(equivalencias[termo_fuzzy_pt], 100.0)]
        
        mapa_scores = {}
        
        if len(termo_fuzzy_pt) >= 4:
            for chave_pt, titulo_en in equivalencias.items():
                tokens_chave = obter_tokens_titulo(chave_pt)
                if termo_fuzzy_pt in tokens_chave:
                    mapa_scores[titulo_en] = max(mapa_scores.get(titulo_en, 0.0), 100.0)
                else:
                    scores_tok = [fuzz.ratio(termo_fuzzy_pt, tok) for tok in tokens_chave if len(tok) >= 4]
                    if scores_tok:
                        max_sc = max(scores_tok)
                        if max_sc >= limite_similaridade:
                            mapa_scores[titulo_en] = max(mapa_scores.get(titulo_en, 0.0), round(max_sc, 1))

        matches = process.extract(
            termo_fuzzy_pt,
            list(equivalencias.keys()),
            scorer=fuzz.WRatio,
            score_cutoff=limite_similaridade,
            limit=20
        )
        for chave_encontrada, score_match, _ in matches:
            titulo_en = equivalencias.get(chave_encontrada)
            if titulo_en:
                mapa_scores[titulo_en] = max(mapa_scores.get(titulo_en, 0.0), round(score_match, 1))
        
        lista_equivalencias = list(mapa_scores.items())
        lista_equivalencias.sort(key=lambda x: x[1], reverse=True)
        return lista_equivalencias
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def calcular_similaridade_tokens(palavras_busca, tokens_titulo):
    if not palavras_busca or not tokens_titulo:
        return 0.0
    melhores_scores = []
    for p in palavras_busca:
        scores = [fuzz.ratio(p, tok) for tok in tokens_titulo if tok]
        if scores:
            melhores_scores.append(max(scores))
        else:
            melhores_scores.append(0.0)
    return sum(melhores_scores) / len(melhores_scores)

def pesquisar_filmes(termo_pesquisa, df_filmes, limite_similaridade=80, limite_resultados=1000):
    if not termo_pesquisa or not termo_pesquisa.strip():
        return []
    
    termo_original = termo_pesquisa.strip().lower()
    lista_equivalencias = resolver_equivalencias(termo_original, limite_similaridade)
    
    # Combina o termo original com as equivalências encontradas.
    itens_busca = [(termo_original, 100.0)]
    for termo_eq, score_eq in lista_equivalencias:
        if termo_eq != termo_original:
            itens_busca.append((termo_eq, score_eq))
    
    # Usa o índice do DataFrame como identificador para evitar filmes duplicados nos resultados.
    resultados_dict = {}
    
    for termo, peso_equivalencia in itens_busca:
        palavras_termo = termo.split()
        
        # Regista correspondências diretas no título, utilizando a pontuação da equivalência como score final.
        for idx, linha in df_filmes.iterrows():
            nome_filme = str(linha["Movie Name"]).lower()
            if termo in nome_filme:
                score_final = round(peso_equivalencia, 1)
                if score_final >= limite_similaridade:
                    if idx not in resultados_dict or score_final > resultados_dict[idx]["score"]:
                        resultados_dict[idx] = criar_filme(linha, score_final)
            else:
                tokens_titulo = obter_tokens_titulo(linha["Movie Name"])
                score_token = calcular_similaridade_tokens(palavras_termo, tokens_titulo)
                score_final = round((peso_equivalencia * score_token) / 100, 1)
                if score_final >= limite_similaridade:
                    if idx not in resultados_dict or score_final > resultados_dict[idx]["score"]:
                        resultados_dict[idx] = criar_filme(linha, score_final)
    
    resultados_pesquisa = list(resultados_dict.values())
    # Ordena os resultados por similaridade decrescente.
    resultados_pesquisa.sort(key=lambda x: x["score"], reverse=True)
    return resultados_pesquisa

# Ordena os resultados segundo o critério selecionado.
def ordenar_filmes(resultados_pesquisa, criterio_ordenacao):
    lista = list(resultados_pesquisa)
    if criterio_ordenacao == "classificacaoDesc":
        lista.sort(key=lambda x: (x["classificacao"] if pd.notna(x["classificacao"]) else -1), reverse=True)
    elif criterio_ordenacao == "classificacaoAsc":
        lista.sort(key=lambda x: (x["classificacao"] if pd.notna(x["classificacao"]) else 999))
    elif criterio_ordenacao == "anoDesc":
        lista.sort(key=lambda x: (x["ano"] if pd.notna(x["ano"]) else -1), reverse=True)
    elif criterio_ordenacao == "anoAsc":
        lista.sort(key=lambda x: (x["ano"] if pd.notna(x["ano"]) else 9999))
    elif criterio_ordenacao == "duracaoDesc":
        lista.sort(key=lambda x: (x["duracao"] if pd.notna(x["duracao"]) else -1), reverse=True)
    elif criterio_ordenacao == "duracaoAsc":
        lista.sort(key=lambda x: (x["duracao"] if pd.notna(x["duracao"]) else 9999))
    elif criterio_ordenacao == "tituloAsc":
        lista.sort(key=lambda x: str(x["titulo"]).lower())
    elif criterio_ordenacao == "tituloDesc":
        lista.sort(key=lambda x: str(x["titulo"]).lower(), reverse=True)
    else:
        lista.sort(key=lambda x: x["score"], reverse=True)
    return lista

# Aplica a ordenação diretamente à coluna selecionada na tabela.
def ordenar_resultados_tabela(resultados_pesquisa, coluna_ordenacao, direcao_ordenacao):
    lista = list(resultados_pesquisa)
    reverso = (direcao_ordenacao == "desc")
    if coluna_ordenacao == "titulo":
        lista.sort(key=lambda x: str(x["titulo"]).lower(), reverse=reverso)
    elif coluna_ordenacao == "classificacao":
        lista.sort(key=lambda x: (x["classificacao"] if pd.notna(x["classificacao"]) else -1), reverse=reverso)
    elif coluna_ordenacao == "ano":
        lista.sort(key=lambda x: (x["ano"] if pd.notna(x["ano"]) else -1), reverse=reverso)
    elif coluna_ordenacao == "duracao":
        lista.sort(key=lambda x: (x["duracao"] if pd.notna(x["duracao"]) else -1), reverse=reverso)
    elif coluna_ordenacao == "similaridade":
        lista.sort(key=lambda x: x["score"], reverse=reverso)
    return lista

def paginar_filmes(lista_filmes, pagina_atual, filmes_por_pagina):
    total_filmes = len(lista_filmes)
    total_paginas = max(1, math.ceil(total_filmes / filmes_por_pagina))
    # Mantém o número da página dentro dos limites disponíveis.
    pagina_ajustada = min(max(1, pagina_atual), total_paginas)
    inicio = (pagina_ajustada - 1) * filmes_por_pagina
    fim = inicio + filmes_por_pagina
    return lista_filmes[inicio:fim], total_paginas, pagina_ajustada

def gerar_cartao_html(filme, idioma, exibir_similaridade=True):
    # Escapa o conteúdo do dataset para impedir que texto seja interpretado como HTML.
    titulo_escapado = html.escape(str(filme["titulo"]))
    descricao_escapada = html.escape(str(filme["descricao"]))
    
    ano_label = traduzir("card.ano", idioma)
    minutos_label = traduzir("card.minutos", idioma)
    similaridade_label = traduzir("card.similaridade", idioma)
    nao_disponivel = traduzir("card.naoDisponivel", idioma)
    
    ano_str = int(filme["ano"]) if pd.notna(filme["ano"]) else nao_disponivel
    classificacao_str = f"{filme['classificacao']}/10" if pd.notna(filme["classificacao"]) else nao_disponivel
    duracao_str = f"{filme['duracao']} {minutos_label}" if pd.notna(filme["duracao"]) else nao_disponivel
    
    linha_similaridade = (
        f'<div class="cartao-linha-similaridade">'
        f'<span class="etiqueta-similaridade">{filme["score"]}% {similaridade_label}</span>'
        f'</div>'
    ) if exibir_similaridade else ""
    
    return (
        f'<div class="cartao-filme">'
        f'<div class="cartao-cabecalho">'
        f'<h3 class="cartao-titulo">{titulo_escapado}</h3>'
        f'</div>'
        f'<div class="cartao-corpo">'
        f'{linha_similaridade}'
        f'<div class="cartao-linha-metadados">'
        f'<span class="etiqueta-classificacao">⭐ {classificacao_str}</span>'
        f'<span class="etiqueta-metadado">📅 {ano_label}: {ano_str}</span>'
        f'<span class="etiqueta-metadado">⏱️ {duracao_str}</span>'
        f'</div>'
        f'<p class="cartao-sinopse">{descricao_escapada}</p>'
        f'</div>'
        f'</div>'
    )

def gerar_tabela_html(filmes_pagina, coluna_ativa, direcao_ativa, idioma, termo_pesquisa=""):
    th_titulo = traduzir("tabela.titulo", idioma)
    th_classificacao = traduzir("tabela.classificacao", idioma)
    th_ano = traduzir("tabela.ano", idioma)
    th_duracao = traduzir("tabela.duracao", idioma)
    th_descricao = traduzir("tabela.descricao", idioma)
    th_similaridade = traduzir("card.similaridade", idioma)
    minutos_label = traduzir("card.minutos", idioma)
    
    # Mostra a coluna de similaridade apenas quando existe uma pesquisa ativa.
    exibir_similaridade = bool(termo_pesquisa.strip())
    param_q = f"&q={termo_pesquisa.strip()}" if exibir_similaridade else ""
    
    def obter_link_coluna(col):
        nova_direcao = "asc" if (col == coluna_ativa and direcao_ativa == "desc") else "desc"
        if col == "titulo" and col != coluna_ativa:
            nova_direcao = "asc"
        seta = ""
        if col == coluna_ativa:
            seta = " ↓" if direcao_ativa == "desc" else " ↑"
        return f"?view=tabela{param_q}&sort_col={col}&sort_dir={nova_direcao}#topo", seta

    link_t, seta_t = obter_link_coluna("titulo")
    link_c, seta_c = obter_link_coluna("classificacao")
    link_a, seta_a = obter_link_coluna("ano")
    link_d, seta_d = obter_link_coluna("duracao")
    link_s, seta_s = obter_link_coluna("similaridade") if exibir_similaridade else ("", "")
    
    c_titulo = " coluna-destacada" if coluna_ativa == "titulo" else ""
    c_class = " coluna-destacada" if coluna_ativa == "classificacao" else ""
    c_ano = " coluna-destacada" if coluna_ativa == "ano" else ""
    c_dur = " coluna-destacada" if coluna_ativa == "duracao" else ""
    c_sim = " coluna-destacada" if coluna_ativa == "similaridade" else ""
    
    nao_disponivel = traduzir("card.naoDisponivel", idioma)
    
    linhas_html = ""
    for filme in filmes_pagina:
        titulo_esc = html.escape(str(filme["titulo"]))
        descricao_esc = html.escape(str(filme["descricao"]))
        class_str = f"{filme['classificacao']}/10" if pd.notna(filme["classificacao"]) else nao_disponivel
        ano_str = int(filme["ano"]) if pd.notna(filme["ano"]) else nao_disponivel
        dur_str = f"{filme['duracao']} {minutos_label}" if pd.notna(filme["duracao"]) else nao_disponivel
        sim_str = f"{filme['score']}%"
        
        td_similaridade = f"<td class='{c_sim.strip()}'>{sim_str}</td>" if exibir_similaridade else ""
        
        linhas_html += (
            f"<tr>"
            f"<td class='{c_titulo.strip()}'><strong>{titulo_esc}</strong></td>"
            f"{td_similaridade}"
            f"<td class='{c_class.strip()}'>{class_str}</td>"
            f"<td class='{c_ano.strip()}'>{ano_str}</td>"
            f"<td class='{c_dur.strip()}'>{dur_str}</td>"
            f"<td>{descricao_esc}</td>"
            f"</tr>"
        )
        
    th_sim_html = f"<th class='{c_sim.strip()}'><a href='{link_s}' target='_self' class='cabecalho-tabela'>{th_similaridade.capitalize()}{seta_s}</a></th>" if exibir_similaridade else ""
    
    return (
        f"<table class='tabela-filmes'>"
        f"<thead><tr>"
        f"<th class='{c_titulo.strip()}'><a href='{link_t}' target='_self' class='cabecalho-tabela'>{th_titulo}{seta_t}</a></th>"
        f"{th_sim_html}"
        f"<th class='{c_class.strip()}'><a href='{link_c}' target='_self' class='cabecalho-tabela'>{th_classificacao}{seta_c}</a></th>"
        f"<th class='{c_ano.strip()}'><a href='{link_a}' target='_self' class='cabecalho-tabela'>{th_ano}{seta_a}</a></th>"
        f"<th class='{c_dur.strip()}'><a href='{link_d}' target='_self' class='cabecalho-tabela'>{th_duracao}{seta_d}</a></th>"
        f"<th>{th_descricao}</th>"
        f"</tr></thead>"
        f"<tbody>{linhas_html}</tbody>"
        f"</table>"
    )

def inicializar_estado_url():
    # Inicializa o estado da sessão com os parâmetros do URL ou com valores por defeito.
    params = st.query_params
    
    idioma_param = params.get("lang", "pt")
    if idioma_param not in {"pt", "en"}:
        idioma_param = "pt"
    if "idioma" not in st.session_state:
        st.session_state["idioma"] = idioma_param

    if "campo_pesquisa" not in st.session_state:
        st.session_state["campo_pesquisa"] = params.get("q", "")

    view_param = params.get("view", "grelha")
    if view_param not in {"grelha", "tabela"}:
        view_param = "grelha"
    if "modo_visualizacao" not in st.session_state:
        st.session_state["modo_visualizacao"] = view_param

    sort_col_param = params.get("sort_col", "classificacao")
    if sort_col_param not in {"titulo", "classificacao", "ano", "duracao", "similaridade"}:
        sort_col_param = "classificacao"
    if "sort_col" not in st.session_state:
        st.session_state["sort_col"] = sort_col_param

    sort_dir_param = params.get("sort_dir", "desc")
    if sort_dir_param not in {"asc", "desc"}:
        sort_dir_param = "desc"
    if "sort_dir" not in st.session_state:
        st.session_state["sort_dir"] = sort_dir_param

    # Define os únicos critérios de ordenação aceites pela aplicação.
    criterios_permitidos = {
        "relevancia", "classificacaoDesc", "classificacaoAsc",
        "anoDesc", "anoAsc", "duracaoDesc", "duracaoAsc",
        "tituloAsc", "tituloDesc"
    }
    default_sort = "relevancia" if st.session_state["campo_pesquisa"] else "classificacaoDesc"
    sort_param = params.get("sort", default_sort)
    if sort_param not in criterios_permitidos:
        sort_param = default_sort
    if "criterio_ordenacao" not in st.session_state:
        st.session_state["criterio_ordenacao"] = sort_param

    try:
        limit_param = int(params.get("limit", 20))
        if limit_param not in {20, 50, 100}:
            limit_param = 20
    except ValueError:
        limit_param = 20
    if "filmes_por_pagina" not in st.session_state:
        st.session_state["filmes_por_pagina"] = limit_param

    try:
        page_param = max(1, int(params.get("page", 1)))
    except ValueError:
        page_param = 1
    if "pagina_atual" not in st.session_state:
        st.session_state["pagina_atual"] = page_param

def ao_mudar_idioma():
    novo_idioma = "pt" if st.session_state["seletor_idioma"] == "Português" else "en"
    st.session_state["idioma"] = novo_idioma
    st.query_params["lang"] = novo_idioma

def ao_mudar_pesquisa():
    valor_pesquisa = st.session_state["campo_pesquisa"]
    st.session_state["pagina_atual"] = 1
    st.query_params["page"] = "1"
    # Reinicia a paginação e sincroniza o termo de pesquisa com os parâmetros do URL.
    if valor_pesquisa.strip():
        st.query_params["q"] = valor_pesquisa
        if "sort" not in st.query_params:
            st.session_state["criterio_ordenacao"] = "relevancia"
            st.query_params["sort"] = "relevancia"
    else:
        if "q" in st.query_params:
            del st.query_params["q"]
        if st.session_state.get("criterio_ordenacao") == "relevancia":
            st.session_state["criterio_ordenacao"] = "classificacaoDesc"
            st.query_params["sort"] = "classificacaoDesc"

def ao_alterar_ordenacao():
    idioma = st.session_state["idioma"]
    chave_widget = f"seletor_ordenacao_{idioma}"
    if chave_widget in st.session_state:
        criterio = st.session_state[chave_widget]
        st.session_state["criterio_ordenacao"] = criterio
        st.query_params["sort"] = criterio

def ao_alterar_por_pagina():
    idioma = st.session_state["idioma"]
    chave_widget = f"seletor_por_pagina_{idioma}"
    if chave_widget in st.session_state:
        limite = st.session_state[chave_widget]
        st.session_state["filmes_por_pagina"] = limite
        st.session_state["pagina_atual"] = 1
        st.query_params["limit"] = str(limite)
        st.query_params["page"] = "1"

def rolar_para_topo():
    token_rolamento = time.time()
    # O script atua no documento principal, pois o componente é executado num iframe.
    st.components.v1.html(
        f"""
        <script data-rolamento-token="{token_rolamento}">
        setTimeout(function() {{
            try {{
                window.parent.document.getElementById('topo').scrollIntoView({{behavior: 'smooth'}});
            }} catch(e) {{
                window.parent.scrollTo(0, 0);
            }}
        }}, 50);
        </script>
        """,
        height=0,
        width=0
    )

def ir_para_pagina(pagina_destino):
    # Centraliza a navegação entre páginas e ativa o regresso ao topo.
    st.session_state["pagina_atual"] = pagina_destino
    st.query_params["page"] = str(pagina_destino)
    st.session_state["deve_rolar_para_topo"] = True

st.set_page_config(
    page_title="IMDb Movies",
    page_icon="🎬",
    layout="wide"
)

carregar_css("style.css")
st.markdown('<div id="topo"></div>', unsafe_allow_html=True)

inicializar_estado_url()
idioma_ativo = st.session_state["idioma"]

titulo_site = traduzir("app.titulo", idioma_ativo)
subtitulo_site = traduzir("app.subtitulo", idioma_ativo)
st.markdown(
    f'<div class="cabecalho-principal">'
    f'<a href="?" target="_self" style="text-decoration: none; color: inherit;"><h1>{titulo_site}</h1></a>'
    f'<p>{subtitulo_site}</p>'
    f'</div>',
    unsafe_allow_html=True
)

df_filmes = carregar_dados()
if df_filmes is None:
    st.error(traduzir("erros.ficheiroNaoEncontrado", idioma_ativo))
    st.stop()

coluna_pesquisa, coluna_modo_visualizacao = st.columns([10, 3])
with coluna_pesquisa:
    termo_pesquisa = st.text_input(
        traduzir("pesquisa.label", idioma_ativo),
        placeholder=traduzir("pesquisa.placeholder", idioma_ativo),
        key="campo_pesquisa",
        on_change=ao_mudar_pesquisa
    )

with coluna_modo_visualizacao:
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        if st.button("🗂️", key="btn_vista_grelha", help=traduzir("visualizacao.grelha", idioma_ativo), use_container_width=True):
            st.session_state["modo_visualizacao"] = "grelha"
            st.query_params["view"] = "grelha"
            st.rerun()
    with col_v2:
        if st.button("📋", key="btn_vista_tabela", help=traduzir("visualizacao.tabela", idioma_ativo), use_container_width=True):
            st.session_state["modo_visualizacao"] = "tabela"
            st.query_params["view"] = "tabela"
            st.rerun()

# Apresenta o catálogo completo ou os resultados da pesquisa.
if termo_pesquisa.strip():
    resultados_brutos = pesquisar_filmes(termo_pesquisa, df_filmes)
    titulo_secao = traduzir("pesquisa.resultadosEncontrados", idioma_ativo)
else:
    resultados_brutos = obter_catalogo_filmes(df_filmes)
    titulo_secao = traduzir("paginacao.catalogoCompleto", idioma_ativo)

if resultados_brutos:
    modo_atual = st.session_state.get("modo_visualizacao", "grelha")
    
    opcoes_ordenacao = {
        "relevancia": traduzir("ordenacao.relevancia", idioma_ativo),
        "classificacaoDesc": traduzir("ordenacao.classificacaoDesc", idioma_ativo),
        "classificacaoAsc": traduzir("ordenacao.classificacaoAsc", idioma_ativo),
        "anoDesc": traduzir("ordenacao.anoDesc", idioma_ativo),
        "anoAsc": traduzir("ordenacao.anoAsc", idioma_ativo),
        "duracaoDesc": traduzir("ordenacao.duracaoDesc", idioma_ativo),
        "duracaoAsc": traduzir("ordenacao.duracaoAsc", idioma_ativo),
        "tituloAsc": traduzir("ordenacao.tituloAsc", idioma_ativo),
        "tituloDesc": traduzir("ordenacao.tituloDesc", idioma_ativo)
    }
    
    criterio_salvo = st.session_state.get("criterio_ordenacao", "classificacaoDesc" if not termo_pesquisa.strip() else "relevancia")
    chaves_ordenacao = list(opcoes_ordenacao.keys())
    index_ordenacao = chaves_ordenacao.index(criterio_salvo) if criterio_salvo in chaves_ordenacao else 0
    
    opcoes_por_pagina = [20, 50, 100]
    limite_salvo = st.session_state.get("filmes_por_pagina", 20)
    index_por_pagina = opcoes_por_pagina.index(limite_salvo) if limite_salvo in opcoes_por_pagina else 0

    with st.container(border=True, key="barra_controlos"):
        if modo_atual == "tabela":
            col_ctrl_1, col_ctrl_3 = st.columns(2)
        else:
            col_ctrl_1, col_ctrl_2, col_ctrl_3 = st.columns(3)
        
        with col_ctrl_1:
            st.selectbox(
                "Idioma / Language",
                options=["Português", "English"],
                index=0 if idioma_ativo == "pt" else 1,
                key="seletor_idioma",
                on_change=ao_mudar_idioma
            )
        
        if modo_atual != "tabela":
            with col_ctrl_2:
                criterio_selecionado = st.selectbox(
                    traduzir("ordenacao.label", idioma_ativo),
                    options=chaves_ordenacao,
                    index=index_ordenacao,
                    format_func=lambda x: opcoes_ordenacao[x],
                    key=f"seletor_ordenacao_{idioma_ativo}",
                    on_change=ao_alterar_ordenacao
                )
        
        with col_ctrl_3:
            filmes_por_pagina = st.selectbox(
                traduzir("paginacao.porPagina", idioma_ativo),
                options=opcoes_por_pagina,
                index=index_por_pagina,
                key=f"seletor_por_pagina_{idioma_ativo}",
                on_change=ao_alterar_por_pagina
            )

    com_pesquisa = bool(termo_pesquisa.strip())
    titulo_exibicao = f"{titulo_secao} ({len(resultados_brutos)})" if com_pesquisa else titulo_secao
    st.subheader(titulo_exibicao)

    if modo_atual == "tabela":
        coluna_ativa = st.session_state.get("sort_col", "classificacao")
        direcao_ativa = st.session_state.get("sort_dir", "desc")
        filmes_ordenados = ordenar_resultados_tabela(resultados_brutos, coluna_ativa, direcao_ativa)
    else:
        criterio_selecionado = st.session_state.get("criterio_ordenacao", "relevancia" if com_pesquisa else "classificacaoDesc")
        filmes_ordenados = ordenar_filmes(resultados_brutos, criterio_selecionado)
    
    pagina_atual = st.session_state.get("pagina_atual", 1)
    filmes_pagina, total_paginas, pagina_atual = paginar_filmes(filmes_ordenados, pagina_atual, filmes_por_pagina)
    st.session_state["pagina_atual"] = pagina_atual

    # Injeta o comando de rolamento apenas depois de uma mudança de página.
    if st.session_state.get("deve_rolar_para_topo", False):
        rolar_para_topo()
        st.session_state["deve_rolar_para_topo"] = False
    
    if modo_atual == "tabela":
        tabela_html = gerar_tabela_html(filmes_pagina, coluna_ativa, direcao_ativa, idioma_ativo, termo_pesquisa)
        st.markdown(tabela_html, unsafe_allow_html=True)
    else:
        cards_html = "".join([gerar_cartao_html(filme, idioma_ativo, exibir_similaridade=com_pesquisa) for filme in filmes_pagina])
        st.markdown(f'<div class="grelha-filmes">{cards_html}</div>', unsafe_allow_html=True)
    
    # Todos os botões de paginação usam a mesma função para manter o estado e o rolamento consistentes.
    if total_paginas > 1:
        col_pag_esq, col_pag_1st, col_pag_mid, col_pag_last, col_pag_dir = st.columns([1.2, 0.8, 2, 0.8, 1.2])
        with col_pag_esq:
            st.button(
                traduzir("paginacao.anterior", idioma_ativo),
                key="btn_pagina_anterior",
                on_click=ir_para_pagina,
                args=(max(1, pagina_atual - 1),),
                disabled=(pagina_atual <= 1),
                use_container_width=True
            )
        with col_pag_1st:
            st.button(
                traduzir("paginacao.primeiraPagina", idioma_ativo),
                key="btn_primeira_pagina",
                on_click=ir_para_pagina,
                args=(1,),
                disabled=(pagina_atual <= 1),
                use_container_width=True
            )
        with col_pag_mid:
            texto_pagina = f"{traduzir('paginacao.pagina', idioma_ativo)} {pagina_atual} {traduzir('paginacao.de', idioma_ativo)} {total_paginas}"
            st.markdown(f"<div class='paginacao-info'>{texto_pagina}</div>", unsafe_allow_html=True)
        with col_pag_last:
            st.button(
                traduzir("paginacao.ultimaPagina", idioma_ativo),
                key="btn_ultima_pagina",
                on_click=ir_para_pagina,
                args=(total_paginas,),
                disabled=(pagina_atual >= total_paginas),
                use_container_width=True
            )
        with col_pag_dir:
            st.button(
                traduzir("paginacao.seguinte", idioma_ativo),
                key="btn_pagina_seguinte",
                on_click=ir_para_pagina,
                args=(min(total_paginas, pagina_atual + 1),),
                disabled=(pagina_atual >= total_paginas),
                use_container_width=True
            )
    
    tooltip_topo = traduzir("app.voltarAoTopo", idioma_ativo)
    st.markdown(f'<a href="#topo" class="botao-voltar-topo" title="{tooltip_topo}">⬆</a>', unsafe_allow_html=True)
else:
    st.subheader(traduzir("pesquisa.resultadosEncontrados", idioma_ativo))
    st.info(traduzir("pesquisa.semResultados", idioma_ativo))