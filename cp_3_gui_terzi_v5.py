import json
import os

# Definição das classes do FIAP BANK

class Conta:
    def __init__(self, numero, titular, saldo=0.0):
        self.numero = numero
        self.titular = titular
        self.saldo = saldo

    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            print(f"Depósito de R${valor:.2f} realizado com sucesso.")
        else:
            print("Valor de depósito inválido.")

    def sacar(self, valor):
        if valor > 0 and self.saldo >= valor:
            self.saldo -= valor
            print(f"Saque de R${valor:.2f} realizado com sucesso.")
            return True
        else:
            print("Saldo insuficiente ou valor inválido para saque.")
            return False

    def transferir(self, valor, conta_destino):
        if self.sacar(valor):
            conta_destino.depositar(valor)
            print(f"Transferência de R${valor:.2f} para a conta {conta_destino.numero} realizada com sucesso.")
            return True
        else:
            return False

    def mostrar_saldo(self):
        print(f"Saldo da conta {self.numero} ({self.titular}): R${self.saldo:.2f}")

    def to_dict(self):
        return {
            "tipo": "conta",
            "numero": self.numero,
            "titular": self.titular,
            "saldo": self.saldo
        }

    @staticmethod
    def from_dict(data):
        return Conta(
            numero=data["numero"],
            titular=data["titular"],
            saldo=data["saldo"]
        )


class ContaCorrente(Conta):
    def __init__(self, numero, titular, saldo=0.0, limite=0.0):
        super().__init__(numero, titular, saldo)
        self.limite = limite  # Limite de cheque especial

    def sacar(self, valor):
        if valor > 0 and (self.saldo + self.limite) >= valor:
            self.saldo -= valor
            print(f"Saque de R${valor:.2f} realizado com sucesso.")
            return True
        else:
            print("Saldo e limite insuficientes para realizar o saque.")
            return False

    def to_dict(self):
        data = super().to_dict()
        data["tipo"] = "corrente"
        data["limite"] = self.limite
        return data

    @staticmethod
    def from_dict(data):
        return ContaCorrente(
            numero=data["numero"],
            titular=data["titular"],
            saldo=data["saldo"],
            limite=data.get("limite", 0.0)
        )


class ContaPoupanca(Conta):
    def __init__(self, numero, titular, saldo=0.0, taxa_juros=0.0):
        super().__init__(numero, titular, saldo)
        self.taxa_juros = taxa_juros  # Taxa de juros mensal

    def aplicar_juros(self):
        juros = self.saldo * self.taxa_juros / 100
        self.saldo += juros
        print(f"Juros de R${juros:.2f} aplicados à conta {self.numero}.")

    def to_dict(self):
        data = super().to_dict()
        data["tipo"] = "poupanca"
        data["taxa_juros"] = self.taxa_juros
        return data

    @staticmethod
    def from_dict(data):
        return ContaPoupanca(
            numero=data["numero"],
            titular=data["titular"],
            saldo=data["saldo"],
            taxa_juros=data.get("taxa_juros", 0.0)
        )

# Funções para salvar e carregar as contas do FIAP BANK

def salvar_contas(contas, arquivo="contas.json"):
    contas_data = [conta.to_dict() for conta in contas]
    with open(arquivo, "w") as f:
        json.dump(contas_data, f, indent=4)
    print("Contas salvas com sucesso.")

def carregar_contas(arquivo="contas.json"):
    if not os.path.exists(arquivo):
        return []

    with open(arquivo, "r") as f:
        contas_data = json.load(f)

    contas = []
    for conta_data in contas_data:
        tipo = conta_data.get("tipo")
        if tipo == "corrente":
            conta = ContaCorrente.from_dict(conta_data)
        elif tipo == "poupanca":
            conta = ContaPoupanca.from_dict(conta_data)
        else:
            conta = Conta.from_dict(conta_data)
        contas.append(conta)

    return contas

# Funções de operação

def criar_conta(contas):
    tipo_conta = input("Digite o tipo de conta (corrente ou poupanca): ").strip().lower()
    numero_conta = input("Digite o número da conta: ").strip()
    titular = input("Digite o nome do titular: ").strip()

    # Verificando se a conta ja existe
    for conta in contas:
        if conta.numero == numero_conta:
            print("Número de conta já existente. Escolha outro número.")
            return

    try:
        saldo_inicial = float(input("Digite o saldo inicial: "))
    except ValueError:
        print("Saldo inicial inválido.")
        return

    if tipo_conta == "corrente":
        try:
            limite = float(input("Digite o limite de cheque especial: "))
        except ValueError:
            print("Limite inválido. Definindo limite como R$0.00.")
            limite = 0.0
        nova_conta = ContaCorrente(numero_conta, titular, saldo_inicial, limite)
    elif tipo_conta == "poupanca":
        try:
            taxa_juros = float(input("Digite a taxa de juros da conta poupança (%): "))
        except ValueError:
            print("Taxa de juros inválida. Definindo taxa de juros como 0%.")
            taxa_juros = 0.0
        nova_conta = ContaPoupanca(numero_conta, titular, saldo_inicial, taxa_juros)
    else:
        print("Tipo de conta inválido.")
        return

    contas.append(nova_conta)
    salvar_contas(contas)
    print("Conta criada com sucesso!")

def depositar(contas):
    numero_conta = input("Digite o número da conta: ").strip()
    try:
        valor = float(input("Digite o valor do depósito: "))
    except ValueError:
        print("Valor inválido para depósito.")
        return

    for conta in contas:
        if conta.numero == numero_conta:
            conta.depositar(valor)
            conta.mostrar_saldo()
            salvar_contas(contas)
            return

    print("Conta não encontrada.")

def sacar(contas):
    numero_conta = input("Digite o número da conta: ").strip()
    try:
        valor = float(input("Digite o valor do saque: "))
    except ValueError:
        print("Valor inválido para saque.")
        return

    for conta in contas:
        if conta.numero == numero_conta:
            if conta.sacar(valor):
                conta.mostrar_saldo()
                salvar_contas(contas)
            return

    print("Conta não encontrada ou saldo insuficiente.")

def transferir(contas):
    numero_conta_origem = input("Digite o número da conta de origem: ").strip()
    numero_conta_destino = input("Digite o número da conta de destino: ").strip()
    try:
        valor = float(input("Digite o valor da transferência: "))
    except ValueError:
        print("Valor inválido para transferência.")
        return

    conta_origem = None
    conta_destino = None

    for conta in contas:
        if conta.numero == numero_conta_origem:
            conta_origem = conta
        if conta.numero == numero_conta_destino:
            conta_destino = conta

    if conta_origem and conta_destino:
        if conta_origem.transferir(valor, conta_destino):
            salvar_contas(contas)
    else:
        print("Conta de origem ou destino não encontrada.")

def mostrar_saldo(contas):
    numero_conta = input("Digite o número da conta: ").strip()
    for conta in contas:
        if conta.numero == numero_conta:
            conta.mostrar_saldo()
            return
    print("Conta não encontrada.")

def aplicar_juros_poupanca(contas):
    for conta in contas:
        if isinstance(conta, ContaPoupanca):
            conta.aplicar_juros()
    salvar_contas(contas)

# Menu principal

def main():
    contas = carregar_contas()

    while True:
        print("\n-$$ FIAP BANK $$-")
        print("1. Criar Conta")
        print("2. Depositar")
        print("3. Sacar")
        print("4. Transferir")
        print("5. Mostrar Saldo")
        print("6. Aplicar Juros Poupança")
        print("7. Sair")

        try:
            opcao = int(input("Digite a opção desejada: "))
        except ValueError:
            print("Digite um número válido.")
            continue

        if opcao == 1:
            criar_conta(contas)
        elif opcao == 2:
            depositar(contas)
        elif opcao == 3:
            sacar(contas)
        elif opcao == 4:
            transferir(contas)
        elif opcao == 5:
            mostrar_saldo(contas)
        elif opcao == 6:
            aplicar_juros_poupanca(contas)
        elif opcao == 7:
            salvar_contas(contas)
            print("Saindo do sistema. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()