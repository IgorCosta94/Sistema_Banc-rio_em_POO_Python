from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime

menu = """
=============================
|| Operações:              ||
|| [d]  Deposito           ||
|| [s]  Saque              ||
|| [e]  Extrato            ||
|| [Nc] Nova Conta         ||
|| [Lc] Listar Contas      ||
|| [Nu] Novo Usuário       ||
|| [x]  Sair               ||
=============================
>>>>"""

class Pessoa:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class ClientePessoaFisica(Pessoa):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class ContaBancaria:
    def __init__(self, numero_conta, titular):
        self._saldo = 0
        self._numero_conta = numero_conta
        self._agencia = "0001"
        self._titular = titular
        self._historico_transacoes = HistoricoConta()

    @classmethod
    def criar_nova_conta(cls, titular, numero_conta):
        return cls(numero_conta, titular)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero_conta(self):
        return self._numero_conta

    @property
    def agencia(self):
        return self._agencia

    @property
    def titular(self):
        return self._titular

    @property
    def historico_transacoes(self):
        return self._historico_transacoes

    def sacar(self, valor):
        current_balance = self.saldo
        excedeu_saldo = valor > current_balance

        if excedeu_saldo:
            print("\nOperação falhou! Saldo insuficiente.")
        elif valor > 0:
            self._saldo -= valor
            print("\nSaque realizado com sucesso!")
            return True
        else:
            print("\nOperação falhou! O valor informado é inválido.")
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\nDepósito realizado com sucesso!")
            return True
        else:
            print("\nOperação falhou! O valor informado é inválido.")
            return False

class ContaCorrente(ContaBancaria):
    def __init__(self, numero_conta, titular, limite_diario=500, max_saques=3):
        super().__init__(numero_conta, titular)
        self.limite_diario = limite_diario
        self.max_saques = max_saques

    def sacar(self, valor):
        num_saques = len(
            [t for t in self.historico_transacoes.transacoes if t["tipo"] == Saque.__name__]
        )

        excedeu_limite_diario = valor > self.limite_diario
        excedeu_max_saques = num_saques >= self.max_saques

        if excedeu_limite_diario:
            print("\nOperação falhou! O valor do saque excede o limite diário.")
        elif excedeu_max_saques:
            print("\nOperação falhou! Número máximo de saques diários atingido.")
        else:
            return super().sacar(valor)
        return False

    def __str__(self):
        return f"""\
            Agência:\t\t{self.agencia}
            C/C:\t\t{self.numero_conta}
            Titular:\t\t{self.titular.nome}
        """

class HistoricoConta:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        transacao_bem_sucedida = conta.sacar(self.valor)

        if transacao_bem_sucedida:
            conta.historico_transacoes.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        transacao_bem_sucedida = conta.depositar(self.valor)

        if transacao_bem_sucedida:
            conta.historico_transacoes.adicionar_transacao(self)

def filtrar_cliente(cpf, clientes):
    """Filtra um cliente por CPF na lista de clientes."""
    for cliente in clientes:
        if isinstance(cliente, ClientePessoaFisica) and cliente.cpf == cpf:
            return cliente
    return None

def recuperar_conta_cliente(cliente, numero_conta):
    """Recupera uma conta específica para um dado cliente."""
    for conta in cliente.contas:
        if conta.numero_conta == numero_conta:
            return conta
    return None

def criar_novo_usuario(clientes):
    """Cria um novo usuário (ClientePessoaFisica) e o adiciona à lista de clientes."""
    cpf = input("\nPor favor! Informe o CPF do cliente (somente números): ")
    cliente = filtrar_cliente(cpf, clientes)
    
    if cliente:
        print("\n######CLIENTE JÁ CADASTRADO!######")
        return 
    
    nome = input("\nNome completo: ")
    data_de_nascimento = input("Data de nascimento (dd-mm-aaaa): ")
    endereco = input("Endereço (logradouro, número - bairro - cidade/sigla do estado): ")

    novo_cliente = ClientePessoaFisica(nome=nome, data_nascimento=data_de_nascimento, cpf=cpf, endereco=endereco)
    clientes.append(novo_cliente)

    print("\n######Cliente cadastrado com sucesso!######")

def criar_contas(agencia, proximo_numero_conta, clientes, contas):
    """Cria uma nova ContaCorrente para um usuário existente."""
    cpf = input("\nInforme o CPF do usuário para associar a conta: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nUSUÁRIO NÃO ENCONTRADO!!!! Não foi possível criar a conta.")
        return None

    nova_conta = ContaCorrente.criar_nova_conta(cliente=cliente, numero_conta=proximo_numero_conta)
    contas.append(nova_conta)
    cliente.adicionar_conta(nova_conta)
    print(f"\nConta {nova_conta.numero_conta} criada com sucesso para {cliente.nome}!")
    return nova_conta

def listar_contas(contas):
    if not contas:
        print("\nNenhuma conta registrada ainda.")
        return

    print("\n=============== CONTAS ===============")
    for conta in contas:
        print("----------------------------------------")
        print(conta) 
    print("========================================")

def listar_clientes(clientes):
    """Lista todos os clientes cadastrados."""
    if not clientes:
        print("\nNenhum cliente registrado ainda.")
        return

    print("\n=============== CLIENTES ===============")
    for cliente in clientes:
        if isinstance(cliente, ClientePessoaFisica):
            print(f"Nome: {cliente.nome}")
            print(f"CPF: {cliente.cpf}")
            print(f"Endereço: {cliente.endereco}")
            print(f"Contas: {[acc.numero_conta for acc in cliente.contas]}")
            print("-----------------------------------")
    print("========================================")

def funcao_principal():
    operacao_invalida = "\nOperação informada inválida, por favor selecione novamente a operação." 

    agencia = "0001"
    clientes = []
    contas = []
    proximo_numero_conta = 1

    while True:
        operacao = input(menu)

        if operacao == "d":
            cpf = input("Informe o CPF do cliente: ")
            cliente = filtrar_cliente(cpf, clientes)

            if not cliente:
                print("\nErro! Cliente não encontrado.")
                continue
            
            numero_conta = int(input("Informe o número da conta para depósito: "))
            conta = recuperar_conta_cliente(cliente, numero_conta)

            if not conta:
                print("\nErro! Conta não encontrada para este cliente.")
                continue

            valor_do_deposito = float(input("\nInforme o valor do depósito: "))
            transacao = Deposito(valor_do_deposito)
            cliente.realizar_transacao(conta, transacao)
        
        elif operacao == "s":
            cpf = input("Informe o CPF do cliente: ")
            cliente = filtrar_cliente(cpf, clientes)

            if not cliente:
                print("\nErro! Cliente não encontrado.")
                continue

            numero_conta = int(input("Informe o número da conta para saque: "))
            conta = recuperar_conta_cliente(cliente, numero_conta)

            if not conta:
                print("\nErro! Conta não encontrada para este cliente.")
                continue

            valor_do_saque = float(input("\nInforme o valor do saque: "))
            transacao = Saque(valor_do_saque)
            cliente.realizar_transacao(conta, transacao)

        elif operacao == "e":
            cpf = input("Informe o CPF do cliente: ")
            cliente = filtrar_cliente(cpf, clientes)

            if not cliente:
                print("\nErro! Cliente não encontrado.")
                continue

            numero_conta = int(input("Informe o número da conta para extrato: "))
            conta = recuperar_conta_cliente(cliente, numero_conta)

            if not conta:
                print("\nErro! Conta não encontrada para este cliente.")
                continue
            
            print("\n================ EXTRATO ================")
            print(f"Conta: {conta.numero_conta}")
            print(f"Titular: {conta.titular.nome}")
            print(f"Saldo: R$ {conta.saldo:.2f}\n")

            if not conta.historico_transacoes.transacoes:
                print("Nenhuma transação registrada.")
            else:
                for t in conta.historico_transacoes.transacoes:
                    print(f"{t['data']} - {t['tipo']}: R$ {t['valor']:.2f}")
            print("============================================")


        elif operacao == "Nu":
            criar_novo_usuario(clientes)

        elif operacao == "Nc":
            conta_criada = criar_contas(agencia, proximo_numero_conta, clientes, contas)
            if conta_criada:
                proximo_numero_conta += 1

        elif operacao == "Lc":
            listar_contas(contas)
            
        elif operacao == "Lp": 
            listar_clientes(clientes)

        elif operacao == "x":
            print("\nSaindo do sistema bancário. Até logo!")
            break

        else:
            print(operacao_invalida)

if __name__ == "__main__":
    funcao_principal()