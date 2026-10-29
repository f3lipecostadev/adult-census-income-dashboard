"""Written findings shown in the last tab.

The figures below describe the full cleaned dataset (48,790 rows, no filters). They are
checked against the data by ``tests/test_findings.py``, so the text cannot silently drift.
The raw string keeps ``\\$`` intact: Streamlit would otherwise read ``$...$`` as a formula.
"""

FINDINGS_MD = r"""
### 1. Distribuições assimétricas

As variáveis mais assimétricas são **capital-gain** (g1 ≈ 11,9) e **capital-loss** (g1 ≈ 4,6),
ambas com cauda à direita. Elas concentram zeros: 91,7% das pessoas não têm ganho de capital e
95,3% não têm perda. Poucos valores altos puxam a média (US\$ 1.080 em *capital-gain*) muito
acima da mediana (0), então a **média não representa o caso típico**. A mediana 0 também diz
pouco; é mais informativo separar quem tem ganho (mediana de US\$ 7.298 entre os 4.035 com
ganho > 0) de quem não tem.

**fnlwgt** (g1 ≈ 1,4) também é assimétrica, mas é um peso amostral do censo, não uma
característica da pessoa. **age** (g1 ≈ 0,56; média 38,7 > mediana 37) tem assimetria positiva
moderada, enquanto **hours-per-week** (0,24) e **education-num** (−0,31) são aproximadamente
simétricas pelo critério |g1| ≤ 0,5. Assimetria indica cauda longa, mas não prova a existência
de outliers.

### 2. Outliers e limitações do critério de Tukey

Pelo critério de Tukey: *hours-per-week* tem 27,6% de outliers (13.486), *capital-gain* 8,3%,
*capital-loss* 4,7%, *education-num* 3,7% (todos abaixo de 4,5, ou seja, escolaridade muito
baixa), *fnlwgt* 3,0% e *age* 0,4% (acima de 78 anos).

Percentuais tão altos mostram a **limitação do método**: em *hours-per-week*, quase metade
(46,7%) trabalha exatamente 40 h, então o IQR é de apenas 5 h e jornadas de meio período ou
longas são marcadas como "outliers", embora sejam comportamentos legítimos. Em *capital-gain* e
*capital-loss* o IQR é 0, então qualquer valor diferente de zero é marcado.

Há ainda um **indício de limitação dos dados**: 244 registros têm *capital-gain* exatamente
99.999 (o valor seguinte mais alto é 41.310) e 54 pessoas têm exatamente 90 anos (contra 2 com
89). Isso sugere valores-teto (censura), uma hipótese que a documentação consultada não
confirma. Nenhum outlier foi removido.

### 3. Correlações

Nenhum par de variáveis numéricas apresenta correlação relevante: todas as correlações de
Pearson são **fracas** (|r| ≤ 0,14) e as de Spearman também (|ρ| ≤ 0,165). As maiores são
*education-num* × *hours-per-week* (r ≈ 0,14; ρ ≈ 0,165), *education-num* × *capital-gain*
(r ≈ 0,13) e *age* × *hours-per-week* (r ≈ 0,07; ρ ≈ 0,15). Com r = 0,14, apenas cerca de 2%
da variação é compartilhada (r²).

O Spearman é um pouco maior que o Pearson em alguns pares (ex.: *age* × *hours-per-week*),
mas continua fraco. Na prática, nenhuma variável numérica sozinha serve para prever outra.
Também é preciso cuidado: *education-num* é ordinal e *fnlwgt* não é um atributo da pessoa. Com
quase 49 mil registros, até correlações pequenas seriam estatisticamente "significativas", mas
isso não as torna relevantes na prática. E correlação não implica causalidade.

### 4. Implicações e cuidados

Na base completa, 23,9% ganham >50K. Quem ganha >50K tem **mediana** de 43 anos (contra 34) e
12 de escolaridade (contra 9); 21,3% deles têm ganho de capital (contra 4,2%). A mediana de
horas é 40 nos dois grupos (a média maior, 45,5 contra 38,8, vem de uma cauda de jornadas
longas).

Um uso possível seria **segmentar o público por faixa etária e escolaridade** (por exemplo,
em um programa de qualificação profissional ou em uma análise de crédito). Isso é uma
associação, não prova que mais estudo causa maior renda, e os dados são de 1994 nos EUA. Como
as correlações numéricas são fracas, uma decisão real deveria considerar também variáveis
categóricas (ocupação, estado civil), que não foram exploradas aqui.
"""
