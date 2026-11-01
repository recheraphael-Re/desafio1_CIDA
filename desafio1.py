"""Desafio 1 CIDA - Raphael Gouvêa Reche - RA 26164063.

Execute: python desafio1.py
Instale a dependência: python -m pip install -r requirements.txt
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Permite gerar imagens sem uma janela gráfica.
import matplotlib.pyplot as plt
import numpy as np


RA = "26164063"
# Transcrição das amostras 16 a 31 do enunciado, na mesma ordem.
rotacao = [382, 560, 767, 838, 495, 1341, 1249, 699,
           436, 885, 583, 773, 796, 591, 455, 1053]
pressao_combustivel = [7.77, 11.73, 7.50, 4.16, 7.38, 6.19, 6.25, 7.33,
                      7.44, 6.35, 6.15, 6.89, 5.40, 7.86, 13.97, 4.21]
temperatura_arrefecimento = [71.62, 70.77, 80.27, 88.78, 73.81, 78.88, 72.57, 87.12,
                            82.40, 81.45, 70.61, 68.24, 77.38, 66.67, 75.81, 75.98]
condicao_motor = [1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0]

# Resumos globais fornecidos no PDF; não recalculados na amostra de 16 dados.
GLOBAL = {"media": 771.79, "desvio": 260.93, "q1": 589, "q3": 868.25}
GRUPOS = {"OK": (529, 635, 786), "Ruim": (733, 845, 1137)}
SAIDA = Path(__file__).resolve().parent / "resultados"


def analisar_temperaturas(valores):
    """Calcula quartis por interpolação linear e outliers pela regra 1,5 IQR."""
    if len(valores) == 0:
        raise ValueError("Informe ao menos uma temperatura.")
    q1, mediana, q3 = np.percentile(valores, [25, 50, 75], method="linear")
    iqr = q3 - q1
    inferior, superior = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return dict(q1=q1, mediana=mediana, q3=q3, iqr=iqr,
                inferior=inferior, superior=superior,
                outliers=[v for v in valores if v < inferior or v > superior],
                altas=sum(v > 90 for v in valores),
                percentual=100 * sum(v > 90 for v in valores) / len(valores))


def gerar_graficos():
    fig, ax = plt.subplots(figsize=(7, 3.8), layout="constrained")
    ax.boxplot([temperatura_arrefecimento], tick_labels=["Amostras 16 a 31"],
               patch_artist=True, boxprops={"facecolor": "#bdd7ee"})
    ax.axhline(90, color="#b22222", linestyle="--", label="Limite de 90 °C")
    ax.set(title="Temperatura de arrefecimento", ylabel="Temperatura (°C)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="lower right")
    fig.savefig(SAIDA / "boxplot_temperatura.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 3.8))
    fig.subplots_adjust(left=0.12, right=0.98, top=0.87, bottom=0.22)
    # Sem extremos/dados brutos globais, não se podem determinar bigodes e outliers.
    # bxp exige whislo/whishi; fixam-se nos quartis e ocultam-se esses elementos.
    resumos = [dict(label=nome, q1=q[0], med=q[1], q3=q[2],
                    whislo=q[0], whishi=q[2], fliers=[])
               for nome, q in GRUPOS.items()]
    ax.bxp(resumos, showfliers=False, showcaps=False, patch_artist=True,
           whiskerprops={"visible": False},
           boxprops={"facecolor": "#bdd7ee"})
    ax.set(title="Rotação por condição do motor - resumo global",
           ylabel="Rotação (RPM)")
    ax.grid(axis="y", alpha=0.25)
    fig.text(0.5, 0.025, "Caixas e medianas; bigodes e outliers não informados no enunciado.",
             ha="center", fontsize=8)
    fig.savefig(SAIDA / "boxplot_rotacao.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    listas = [rotacao, pressao_combustivel, temperatura_arrefecimento, condicao_motor]
    if any(len(lista) != 16 for lista in listas):
        raise ValueError("As quatro listas devem conter 16 valores.")
    if RA[-1] != "3":
        raise ValueError("As listas foram selecionadas para RA terminado em 3.")
    SAIDA.mkdir(exist_ok=True)
    r = analisar_temperaturas(temperatura_arrefecimento)
    gerar_graficos()
    linhas = ["Desafio 1 - CIDA", "Raphael Gouvêa Reche | RA 26164063",
              "a) Amostras 16 a 31 (16 observações).",
              "Amostra | RPM | Pressão combustível | Temperatura (°C) | Condição"]
    for numero, valores in enumerate(zip(*listas), start=16):
        rpm, pressao, temperatura, condicao = valores
        linhas.append(f"{numero:2d} | {rpm:4d} | {pressao:5.2f} | {temperatura:5.2f} | {condicao}")
    linhas += [
        f"b) Q1 = {r['q1']:.4f}; mediana = {r['mediana']:.4f}; Q3 = {r['q3']:.4f} °C.",
        f"IQR = {r['iqr']:.4f}; limites = [{r['inferior']:.4f}, {r['superior']:.4f}] °C.",
        f"Outliers: {r['outliers']} (regra 1,5 IQR).",
        f"c) Temperaturas acima de 90 °C: {r['altas']}/16 = {r['percentual']:.2f}%.",
        "d) Mediana OK = 635 RPM; ruim = 845 RPM. Diferença = 210 RPM.",
        "Observa-se rotação maior no grupo ruim, mas com sobreposição das caixas.",
        "Não se determina causalidade nem diagnóstico apenas pela rotação.",
        "Sem extremos globais, representam-se apenas caixas e medianas.",
        f"e) Média +/- desvio: [{GLOBAL['media'] - GLOBAL['desvio']:.2f}, "
        f"{GLOBAL['media'] + GLOBAL['desvio']:.2f}] RPM.",
        "A cobertura de aproximadamente 68% pressupõe distribuição aproximadamente normal.",
        f"f) 50% centrais: [{GLOBAL['q1']:.2f}, {GLOBAL['q3']:.2f}] RPM.",
        "O intervalo interquartil descreve os 50% centrais; não necessariamente os mais prováveis.",
    ]
    texto = "\n".join(linhas) + "\n"
    (SAIDA / "respostas.txt").write_text(texto, encoding="utf-8")
    print(texto)
    print(f"Gráficos e respostas gravados em: {SAIDA}")


if __name__ == "__main__":
    main()
