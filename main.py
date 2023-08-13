import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, value
from tabulate import tabulate


# Função para converter DataFrame para lista de dicionários
def dataframe_to_list(dataframe):
    return dataframe.to_dict("records")


# Dados com as opções de investimento
tabela_de_investimentos = pd.read_csv("investimentos.csv")
investimentos = dataframe_to_list(tabela_de_investimentos)

# Limites de custo
limite_de_custos_total = 2400000
limite_de_custos_por_risco = {"Baixo": 1200000, "Médio": 1500000, "Alto": 900000}
minimo_por_risco = {"Baixo": 2, "Médio": 2, "Alto": 1}


def retorno_maximo(investimentos):
    # Definindo o problema que precisa ser maximizado.
    problema = LpProblem("RetornoMáximo", LpMaximize)

    # As variáveis de decisão
    invest_vars = {}
    for investimento in investimentos:
        invest_vars[investimento["opcao"]] = LpVariable(f"Invest_{investimento['opcao']}", cat="Binary")
        if investimento["custo"] < 0:
            raise ValueError(f"O custo do investimento {investimento['opcao']} é negativo.")
        if investimento["retorno"] < 0:
            raise ValueError(f"O retorno do investimento {investimento['opcao']} é negativo.")

    # Função objetivo
    problema += lpSum([investimento["retorno"] * invest_vars[investimento["opcao"]] for investimento in investimentos]), "Retorno Total"

    # Restrições de custo

    problema += (
        lpSum([investimento["custo"] * invest_vars[investimento["opcao"]] for investimento in investimentos]) <= limite_de_custos_total,
        "Custo Total Máximo",
    )

    for tipo_de_risco, limite_custo in limite_de_custos_por_risco.items():
        problema += (
            lpSum(
                [
                    investimento["custo"] * invest_vars[investimento["opcao"]]
                    for investimento in investimentos
                    if investimento["risco"] == tipo_de_risco
                ]
            )
            <= limite_custo,
            f"Custo limite de risco {tipo_de_risco}",
        )

    # Restrições de quantidade minima por tipo de risco

    problema += (
        lpSum([invest_vars[investimento["opcao"]] for investimento in investimentos if investimento["risco"] == "Alto"]) 
        >= minimo_por_risco["Alto"],
        "Investimento Alto Minimo",
    )
    problema += (
        lpSum([invest_vars[investimento["opcao"]] for investimento in investimentos if investimento["risco"] == "Médio"])
        >= minimo_por_risco["Médio"],
        "Investimento Médio Minimo",
    )
    problema += (
        lpSum([invest_vars[investimento["opcao"]] for investimento in investimentos if investimento["risco"] == "Baixo"])
        >= minimo_por_risco["Baixo"],
        "Investimento Baixo Minimo",
    )

    # Resolução do problema usando o pulp e CBC
    problema.solve()

    resultados = [investimento for investimento in investimentos if value(invest_vars[investimento["opcao"]]) == 1]
    colunas = ["opcao", "descricao", "custo", "retorno", "risco"]

    df = pd.DataFrame(resultados, columns=colunas)

    print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))

    total_retorno = value(problema.objective)
    total_investido = sum(investimento["custo"] for investimento in resultados)
    total_investido_formatted = "{:,.0f}".format(total_investido)
    total_retorno_formatted = "{:,.0f}".format(total_retorno)

    print(f"Valor Total Investido: R$ {total_investido_formatted}")
    print(f"Valor Total de Retorno: R$ {total_retorno_formatted}")

    # Calculo do total de custo por tipo de risco
    total_cost_by_risk = {}
    for investimento in resultados:
        risco = investimento["risco"]
        custo = investimento["custo"]
        total_cost_by_risk[risco] = total_cost_by_risk.get(risco, 0) + custo

    # Print do total de custo por tipo de risco
    print("Custo Total Por Risco: ", end="")
    for risco, custo in total_cost_by_risk.items():
        custo_formatted = "{:,.0f}".format(custo)
        print(f"{risco}: R$ {custo_formatted} ", end="")

    return resultados, value(problema.objective)


resultados, valor = retorno_maximo(investimentos)


# Charts de análize
def plot_custos_retornos_investimentos(resultados):
    investimentos = [investimento["descricao"] for investimento in resultados]
    custos = [investimento["custo"] for investimento in resultados]
    retornos = [investimento["retorno"] for investimento in resultados]

    bar_width = 0.35
    index = np.arange(len(investimentos))

    plt.figure(figsize=(12, 6))
    plt.bar(index, custos, bar_width, label="Custos")
    plt.bar(index + bar_width, retornos, bar_width, label="Retornos")
    plt.xlabel("Investimentos")
    plt.ylabel("Valor")
    plt.title("Custos e Retornos dos Investimentos")
    plt.xticks(index + bar_width / 2, investimentos, rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_custos_retornos_por_risco(resultados):
    riscos = ["Baixo", "Médio", "Alto"]
    custos_totais = [sum([investimento["custo"] for investimento in resultados if investimento["risco"] == risco]) for risco in riscos]
    retornos_totais = [sum([investimento["retorno"] for investimento in resultados if investimento["risco"] == risco]) for risco in riscos]

    bar_width = 0.35
    index = np.arange(len(riscos))

    plt.figure(figsize=(10, 6))
    plt.bar(index, custos_totais, bar_width, label="Custos")
    plt.bar(index + bar_width, retornos_totais, bar_width, label="Retornos")
    plt.xlabel("Tipo de Risco")
    plt.ylabel("Valor Total")
    plt.title("Custos e Retornos Totais por Tipo de Risco")
    plt.xticks(index + bar_width / 2, riscos)
    plt.legend()

    for i, valor in enumerate(custos_totais):
        plt.text(i, valor, f"R${valor:,.2f}\n({valor / sum(custos_totais) * 100:.1f}%)", ha="center", va="bottom")
    for i, valor in enumerate(retornos_totais):
        plt.text(i + bar_width, valor, f"R${valor:,.2f}\n({valor / sum(retornos_totais) * 100:.1f}%)", ha="center", va="bottom")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    plot_custos_retornos_investimentos(resultados)
    plot_custos_retornos_por_risco(resultados)
