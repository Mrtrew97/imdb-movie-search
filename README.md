# Motor de Pesquisa de Filmes IMDb

Aplicação interativa de pesquisa desenvolvida como projeto final do curso de Programação em Python da Master.D.
A aplicação permite explorar e pesquisar o ranking dos 1000 melhores filmes do IMDb, utilizando correspondência aproximada (*fuzzy matching*) e uma interface web interativa.


## Objetivos

O projeto aplica conceitos fundamentais de programação em Python e manipulação de dados, destacando as seguintes competências:

- **Importação e manipulação de dados** com a biblioteca `pandas`.
- **Limpeza e tratamento dos dados** importados.
- **Implementação de pesquisa aproximada** com a biblioteca `rapidfuzz`.
- **Desenvolvimento de uma interface web interativa** com a biblioteca `streamlit`.
- **Implementação de pesquisa por equivalências linguísticas** entre títulos em português de Portugal e os respetivos títulos originais em inglês.
- **Gestão de estado e parâmetros de URL** para preservar a navegação e as preferências de utilização.
- **Aplicação de boas práticas de organização e desenvolvimento** em Python.


## Tecnologias utilizadas

- **Python**: linguagem principal de programação.
- **pandas**: manipulação e análise do conjunto de dados.
- **rapidfuzz**: correspondência aproximada de texto, com tolerância a erros de escrita.
- **Streamlit**: construção da interface web interativa.


## Estrutura do dataset

O projeto utiliza o ficheiro `top_1000_imdb_movies.csv`, composto pelas seguintes colunas principais:

- **Movie Name**: título do filme.
- **Year of Release**: ano de lançamento do filme, tratado para remover valores não numéricos.
- **Watch Time**: duração do filme em minutos.
- **Movie Rating**: classificação do filme no IMDb.
- **Description**: breve sinopse do filme.


## Estrutura do projeto

```text
.
├── app.py
├── requirements.txt
├── top_1000_imdb_movies.csv
├── style.css
├── README.md
├── locales/
│   ├── pt.json
│   ├── en.json
│   └── equivalencias_pt.json
└── .streamlit/
    └── config.toml
```

- `app.py`: contém a lógica principal da aplicação, o motor de pesquisa, o processamento dos dados e a interface Streamlit.
- `requirements.txt`: lista as dependências necessárias para a execução do projeto.
- `top_1000_imdb_movies.csv`: contém os dados dos filmes utilizados pelo catálogo.
- `style.css`: define os estilos visuais e a identidade gráfica da aplicação.
- `locales/pt.json` e `locales/en.json`: contêm os textos da interface traduzidos para português e inglês.
- `locales/equivalencias_pt.json`: contém o dicionário de equivalências de títulos e expressões em português de Portugal, utilizado pelo motor de pesquisa para estabelecer correspondências com os títulos originais em inglês.
- `.streamlit/config.toml`: define configurações base e parâmetros do tema visual da aplicação.


## Instalação e execução

1. Clonar ou descarregar o repositório para a máquina local.
2. Abrir o terminal na pasta raiz do projeto.
3. Instalar as dependências:

```bash
pip install -r requirements.txt
```

4. Iniciar a aplicação:
```bash
python -m streamlit run app.py
```

5. Aceder ao endereço apresentado no terminal:
```text
http://localhost:8501
```


## Robustez e tratamento de dados

A aplicação foi desenvolvida com atenção à qualidade e à experiência do utilizador. O carregamento do dataset é feito com `pandas` através de uma função dedicada e com `@st.cache_data`, reduzindo leituras repetidas e melhorando o desempenho. Quando o ficheiro não existe, a aplicação apresenta uma mensagem informativa em vez de um erro técnico.

Além disso, o processo de limpeza inclui a remoção da coluna `Unnamed: 0`, a eliminação de duplicados, a normalização de títulos e descrições com `str.strip()`, a conversão do ano com expressão regular e `errors="coerce"`, e ainda o tratamento seguro de valores ausentes e de conteúdo HTML antes da apresentação na interface.

## Funcionalidades principais

- **Pesquisa híbrida e aproximada**: encontra filmes mesmo quando o título introduzido não corresponde exatamente ao título presente no dataset, combinando correspondência direta com diferentes estratégias de *fuzzy matching* através da biblioteca `rapidfuzz`.
- **Equivalências em Português (PT-PT)**: permite pesquisar utilizando títulos e expressões conhecidas em português de Portugal, resolvendo essas referências para os títulos originais em inglês através do ficheiro `equivalencias_pt.json`. As pontuações das equivalências são combinadas com as pontuações obtidas na pesquisa dos títulos.
- **Tolerância a erros de escrita**: utiliza algoritmos de correspondência aproximada para identificar títulos semelhantes, mesmo quando existem gralhas, diferenças de escrita ou pequenas variações no termo pesquisado.
- **Catálogo completo**: apresenta todos os filmes disponíveis quando a barra de pesquisa está vazia, utilizando a classificação como critério de ordenação predefinido.
- **Multilinguismo (PT / EN)**: permite alternar dinamicamente entre português e inglês através de ficheiros JSON externos, mantendo a interface traduzida sem alterar a lógica da aplicação.
- **Modos de visualização**: permite alternar entre uma apresentação em cartões (*Grid View*) e uma apresentação detalhada em tabela (*Table View*).
- **Ordenação dinâmica**: na vista em cartões, permite ordenar os resultados por relevância, classificação, ano, duração ou título, em ordem ascendente ou descendente.
- **Ordenação interativa na tabela**: permite ordenar diretamente os resultados através dos cabeçalhos das colunas, apresentando uma indicação visual da direção da ordenação e destacando a coluna atualmente selecionada.
- **Paginação**: permite escolher entre 20, 50 ou 100 filmes por página.
- **Navegação avançada**: disponibiliza controlos para navegar para a primeira, anterior, seguinte ou última página, juntamente com um botão flutuante para regressar ao topo da página.
- **Persistência de estado no URL**: sincroniza os principais parâmetros da aplicação através de `st.query_params`, incluindo o termo de pesquisa, página atual, modo de visualização, idioma e critérios de ordenação, permitindo manter e partilhar diferentes estados da aplicação através do URL.
- **Cache de dados e traduções**: utiliza `st.cache_data` para evitar o carregamento e processamento desnecessário do dataset e dos ficheiros de tradução durante as reexecuções da aplicação.
- **Proteção do conteúdo HTML**: utiliza `html.escape()` para impedir que títulos e descrições provenientes do dataset sejam interpretados diretamente como código HTML.


## Pesquisa e sistema de relevância

O motor de pesquisa utiliza várias estratégias complementares para obter resultados relevantes:

1. **Correspondência direta** — verifica se o termo pesquisado está presente no título do filme.
2. **Correspondência por palavras** — divide o termo pesquisado em palavras e compara cada uma individualmente com os tokens existentes nos títulos, calculando uma pontuação média de similaridade.
3. **Correspondência aproximada (`WRatio`)** — permite identificar títulos semelhantes mesmo perante erros de escrita ou diferenças na composição do texto.
4. **Equivalências linguísticas** — procura correspondências no dicionário `equivalencias_pt.json`, permitindo relacionar termos em português de Portugal com títulos originais em inglês.
5. **Combinação de pontuações** — quando são utilizadas equivalências, a pontuação da equivalência é combinada com a pontuação obtida na correspondência com o título, permitindo determinar uma percentagem final de similaridade.

Os resultados são posteriormente deduplicados e ordenados pela maior pontuação de similaridade obtida para cada filme.


## Interface

A interface foi desenvolvida com Streamlit e personalizada através de CSS externo.

A aplicação disponibiliza:

- Barra de pesquisa;
- Seletor de idioma;
- Alternância entre vista em grelha e tabela;
- Diferentes critérios de ordenação;
- Seleção do número de resultados por página;
- Indicadores de similaridade;
- Classificação, ano e duração dos filmes;
- Paginação;
- Navegação através de parâmetros no URL;
- Botão de regresso ao topo da página.



## Licença

Projeto desenvolvido para fins académicos no âmbito do curso de Programação em Python da Master.D.