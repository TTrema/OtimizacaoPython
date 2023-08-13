import unittest
from main import retorno_maximo, limite_de_custos_total, investimentos, limite_de_custos_por_risco, minimo_por_risco
import random

# Cria investimentos de valores aleatórios para testes
investimentos_3000 = []
for i in range(3000):
    investimento = {
        "opcao": i + 1,
        "custo": random.randint(100000, 500000),
        "retorno": random.randint(50000, 400000),
        "risco": random.choice(["Baixo", "Médio", "Alto"]),
        "descricao": f"Investimento fictício {i + 1}"
    }
    investimentos_3000.append(investimento)

class TestInvestmentSelection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resultados, cls.objective_value = retorno_maximo(investimentos)
        
    def test_custo_total_maximo(self):
        custo_total = sum([investimento["custo"] for investimento in self.resultados])
        self.assertLessEqual(custo_total, limite_de_custos_total)

    def test_quantidade_risco_alto_minimo(self):
        investimentos_de_alto_risco = sum([1 for investimento in self.resultados if investimento["risco"] == "Alto"])
        self.assertGreaterEqual(investimentos_de_alto_risco, minimo_por_risco["Alto"])

    def test_quantidade_risco_medio_minimo(self):
        investimentos_de_medio_risco = sum([1 for investimento in self.resultados if investimento["risco"] == "Médio"])
        self.assertGreaterEqual(investimentos_de_medio_risco, minimo_por_risco["Médio"])

    def test_quantidade_risco_baixo_minimo(self):
        investimentos_de_baixo_risco = sum([1 for investimento in self.resultados if investimento["risco"] == "Baixo"])
        self.assertGreaterEqual(investimentos_de_baixo_risco, minimo_por_risco["Baixo"])

    def test_custo_maximo_por_tipo_de_risco(self):
        for tipo_de_risco, limite_custo in limite_de_custos_por_risco.items():
            custo_total_do_tipo_de_risco = sum([investimento["custo"] for investimento in self.resultados if investimento["risco"] == tipo_de_risco])
            self.assertLessEqual(custo_total_do_tipo_de_risco, limite_custo)

    def test_assert_investimento_com_custo_negativo(self):
        investimentos_custo = investimentos.copy()
        investimentos_custo.append(
            {"opcao": 100, "custo": -100000, "retorno": 50000, "risco": "Baixo", "descricao": "Investimento com custo negativo"}
        )
        with self.assertRaises(ValueError) as context:
            retorno_maximo(investimentos_custo)
        self.assertEqual(str(context.exception), "O custo do investimento 100 é negativo.")

    def test_assert_investimento_com_retorno_negativo(self):
        investimentos_retorno = investimentos.copy()
        investimentos_retorno.append(
            {"opcao": 100, "custo": 100000, "retorno": -50000, "risco": "Baixo", "descricao": "Investimento com custo negativo"}
        )
        with self.assertRaises(ValueError) as context:
            retorno_maximo(investimentos_retorno)
        self.assertEqual(str(context.exception), "O retorno do investimento 100 é negativo.")

class TestInvestmentSelectio3000(unittest.TestCase):
    def setUp(self):
        self.resultados_3000, self.objective_value_3000 = retorno_maximo(investimentos_3000)
    def test_de_escalabilidade(self):        
        custo_total = sum([investimento["custo"] for investimento in self.resultados_3000])
        self.assertLessEqual(custo_total, limite_de_custos_total)        

if __name__ == "__main__":
    unittest.main()
