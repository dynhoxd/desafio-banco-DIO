import datetime
import json
import textwrap
from functools import wraps
from pathlib import Path

ROOT_PATH = Path(__file__).parent

# class ContaIterator:
#     def __init__(self, contas):
#         self.contas = contas
#         self.contador = 0

#     def __iter__(self):
#         return self

#     def __next__(self):
#         try:
#             conta = self.contas[self.contador]
#             self.contador += 1
#             return conta
#         except IndexError:
#             raise StopIteration


def decorador_log(func):
    @wraps(func)
    def faz_log(*args, **kwargs):
        now = datetime.datetime.now()
        f = func(*args, **kwargs)
        cpf = getattr(args[0], "cpf", None) #if args else None
        args_nomeados = kwargs.copy()
        if "cpf" in args_nomeados:
            del args_nomeados["cpf"]
        try:
            with open(ROOT_PATH / "log.txt", "a", encoding="utf-8") as arquivo_log:
                if cpf:
                    arquivo_log.write(
                        f"{now:%d/%m/%Y %H:%M:%S}, "
                        f"cliente de cpf {cpf}, "
                        f"fez a ação de {func.__name__} "
                        f"com os argumentos: [{args_nomeados}]\n"
                    )
                else:
                    arquivo_log.write(
                        f"{now:%d/%m/%Y %H:%M:%S}, "
                        f"Foi executada a ação de {func.__name__}\n"
                    )
        except Exception as exc:
            print(f"Erro ao tentar registrar a ação.\nErro:{exc}")
        return func.__name__

    return faz_log


def menu():
    opcoes = {
        "d": "Depositar",
        "s": "Sacar",
        "es": "Exibir Saldo",
        "e": "Extrato",
        "ru": "Registrar Usuário",
        "rc": "Registrar Conta",
        "lu": "Listar Usuários",
        "lc": "Listar Contas",
        "du": "Deletar Usuário",
        "dc": "Deletar Conta",
        "x": "Sair",
    }
    print("MENU DE OPERAÇÕES".center(40, "="))
    for chave, descricao in opcoes.items():
        print(f"[{chave:2}] - {descricao}")
    print("=" * 40)
    return input("Escolha uma opção: ")


try:
    with open(ROOT_PATH / "clientes.json", "r", encoding="utf-8") as arquivo_clientes:
        ref_clientes = json.load(arquivo_clientes)
except:
    ref_clientes = {}

try:
    with open(ROOT_PATH / "contas.json", "r", encoding="utf-8") as arquivo_contas:
        ref_contas = json.load(arquivo_contas)
except:
    ref_contas = {}


class Transacoes:
    def __init__(self, contas):
        self.contas = contas

    @decorador_log
    def depositar(self, conta, valor):
        self.cpf = self.contas[conta]["cpf"]
        self.contas[conta]["saldo"] += valor
        self.salvar_atualizacoes()

    @decorador_log
    def sacar(self, conta, valor):
        # self.cpf = self.contas[conta]["cpf"]
        dados = self.contas.get(conta)
        if valor > dados.get("saldo"):
            raise ValueError("\nSaldo insuficiente")
        elif valor > dados.get("limite_valor_saque_dia"):
            raise ValueError("\nLimite de valor diário excedido")
        elif dados.get("saques_efetuados_hoje") == 10:
            raise ValueError("\nLimite de saques diários excedido")
        else:
            dados["saldo"] -= valor
            dados["saques_efetuados_hoje"] += 1
            dados["limite_valor_saque_dia"] -= valor
            self.salvar_atualizacoes()

    def salvar_atualizacoes(self):
        try:
            with open(
                ROOT_PATH / "contas.json", "w", encoding="utf-8"
            ) as arquivo_contas:
                json.dump(self.contas, arquivo_contas, indent=2)
        except IOError as exc:
            print(
                f"\nErro ao tentar salvar as atualizações no arquivo de contas: {exc}"
            )


class Banco:
    agencia = "0001"

    def __init__(self, clientes, contas):
        self.clientes = clientes
        self.contas = contas

    def verificar_conta(self, conta):
        return conta in self.contas

    def verificar_cpf(self, cpf):
        return cpf in self.clientes

    @decorador_log
    def registrar_usuario(self, novo_cliente):
        # self.cpf = self.contas[novo_cliente["cpf"]]
        self.clientes[novo_cliente["cpf"]] = {
            "nome": novo_cliente["nome"],
            "data_nascimento": novo_cliente["data_nascimento"],
            "endereco": novo_cliente["endereco"],
            "contas": [],
        }
        self.salvar_atualizacoes()

    @decorador_log
    def registrar_conta(self, cpf):
        numeros_contas = [int(n) for n in self.contas.keys() if str(n).isdigit()]
        maior_conta = max(numeros_contas) if numeros_contas else 0
        numero_conta = maior_conta + 1
        titular = self.clientes.get(cpf).get("nome")
        self.contas[numero_conta] = {
            "agencia": Banco.agencia,
            "saldo": 0,
            "limite_valor_saque_dia": 500,
            "saques_efetuados_hoje": 0,
            "titular": titular,
            "cpf": cpf,
        }
        self.clientes.get(cpf).get("contas").append(
            {"agencia": Banco.agencia, "numero_conta": numero_conta}
        )
        self.salvar_atualizacoes()

    @decorador_log
    def listar_contas(self):
        for numero_conta, conta in self.contas.items():
            if numero_conta != "0":
                print(
                    textwrap.dedent(
                        f"""\n
                    Conta: {numero_conta}\n
                    Agência: {conta["agencia"]}\n
                    Saldo: R$ {conta["saldo"]:.2f}\n
                    Limite disponível para saque hoje: R$ {conta["limite_valor_saque_dia"]:.2f}\n
                """
                    )
                )

    @decorador_log
    def listar_usuarios(self):
        for cpf, usuario in self.clientes.items():
            print(
                textwrap.dedent(f"""\n
                nome: {usuario["nome"]}
                cpf: {cpf}
                data de nascimento: {usuario["data_nascimento"]}
                endereço: {usuario["endereco"]}
                contas: """)
            )
            for conta in usuario["contas"]:
                print(f"""
                agência: {conta["agencia"]:>12}
                numero da conta: {conta["numero_conta"]:>4}
                """)
            print("\n----------------------------------------\n")

    @decorador_log
    def exibir_saldo(self, conta_informada):
        self.cpf = self.contas[conta_informada]["cpf"]
        print(
            f"\nO saldo da conta {conta_informada} é R$ {self.contas[conta_informada]['saldo']:.2f}"
        )
    
    @decorador_log
    def deletar_usuario(self, cpf):
        self.clientes.pop(cpf, None)
        self.salvar_atualizacoes()

    @decorador_log
    def deletar_conta(self, conta):
        cpf = self.contas[conta]["cpf"]
        self.contas.pop(conta, None)
        lista_contas = self.clientes[cpf]["contas"]
        for i, conta_cadastrada in enumerate(lista_contas):
            if conta_cadastrada["numero_conta"] == int(conta):
                lista_contas.pop(i)

        self.salvar_atualizacoes()


    def salvar_atualizacoes(self):
        try:
            with open(
                ROOT_PATH / "clientes.json", "w", encoding="utf-8"
            ) as arquivo_clientes:
                json.dump(self.clientes, arquivo_clientes, indent=2)
        except IOError as exc:
            print(
                f"\nErro ao tentar salvar as atualizações no arquivo de cliente: {exc}"
            )

        try:
            with open(
                ROOT_PATH / "contas.json", "w", encoding="utf-8"
            ) as arquivo_contas:
                json.dump(self.contas, arquivo_contas, indent=2)
        except IOError as exc:
            print(
                f"\nErro ao tentar salvar as atualizações no arquivo de contas: {exc}"
            )


def main():
    meu_banco = Banco(ref_clientes, ref_contas)
    fazer_transacao = Transacoes(ref_contas)

    while True:
        opcao = menu().lower()
        if opcao == "d":
            conta_informada = input("Informe o número da conta para depósito: ")
            if not meu_banco.verificar_conta(conta_informada):
                print("Conta não encontrada")
                continue
            valor_str = input("Informe o valor do depósito ou digite x para voltar: ")
            if valor_str.lower() == "x":
                continue
            try:
                valor = int(valor_str)
                if valor < 0:
                    print("Valores negativos não são permitidos")
                    continue
            except:
                print("Valor inválido. \nDigite um número!")
                continue
            fazer_transacao.depositar(conta=conta_informada, valor=float(valor_str))
            print(
                f"\nO depósito de €{valor} na conta {conta_informada} foi realizado com sucesso"
            )

        elif opcao == "s":
            conta_informada = input("Informe o número da conta para saque: ")
            if not meu_banco.verificar_conta(conta_informada):
                print("Conta não encontrada")
                continue
            valor_str = input("Informe o valor do saque ou digite x para voltar: ")
            if valor_str.lower() == "x":
                continue
            try:
                valor = int(valor_str)
                if valor < 0:
                    print("Valores negativos não são permitidos")
                    continue
            except:
                print("Valor inválido. \nDigite um número!")
                continue
            try:
                fazer_transacao.sacar(conta=conta_informada, valor=valor)
                print(
                    f"\nO saque de €{valor_str} da conta {conta_informada} foi realizado com sucesso"
                )
            except ValueError as e:
                print(e)
            except Exception as e:
                print(f"Aconteceu o seguinte erro ao tentar fazer o saque: {e}")

        elif opcao == "e":
            pass
            # conta = int(input("Informe o número da conta para exibir o extrato: "))
            # if conta not in [c["numero_conta"] for c in contas]:
            #     print("Conta não encontrada.")
            #     continue
            # elif conta not in extrato:
            #     print("\nNão foram realizadas movimentações para essa conta.")
            #     continue
            # else:
            #     saldo = next(c["saldo"] for c in contas if c["numero_conta"] == conta)
            #     # for c in contas:
            #     #     if c["numero_conta"] == conta:
            #     #         saldo = c["saldo"]
            #     tipo_operacao = input(
            #         "\n\nDeseja filtrar o extrato por tipo de operação?\n\n (d) Depósitos\n (s) Saques\n"
            #         "       Ou pressione Enter para exibir todos\n\n => "
            #     ).lower()
            #     exibir_extrato(
            #         saldo, extrato=extrato, conta=conta, tipo_operacao=tipo_operacao
            # )

        elif opcao == "ru":
            cpf = input("Informe o número do cpf ou x para voltar: ")
            if cpf.lower() == "x":
                continue
            elif not cpf.isdigit():
                print("\nApenas números são aceites")
                continue
            elif meu_banco.verificar_cpf(cpf):
                print("\nEste CPF já está associado a um usuário")
                continue
            else:
                nome = input("Informe o nome do novo cliente: ")
                data_nascimento = input(
                    "Informe a data de nascimento do novo cliente (DD-MM-AAAA): "
                )
                endereco = input(
                    "Informe o endereço do novo cliente (logradouro, número - bairro - cidade/sigla estado): "
                )
                novo_cliente = {
                    "cpf": cpf,
                    "nome": nome,
                    "data_nascimento": data_nascimento,
                    "endereco": endereco,
                }
                meu_banco.registrar_usuario(novo_cliente)
                print("\nUsuário registrado com sucesso")

        elif opcao == "rc":
            cpf = input(
                "\nInforme o cpf do usuário titular da nova conta ou x para voltar: "
            )
            if cpf.lower() == "x":
                continue
            elif not cpf.isdigit():
                print("\nDigite apenas números")
                continue
            elif not meu_banco.verificar_cpf(cpf):
                print("\nÉ necessário cadastrar o cliente antes de criar uma conta")
                continue
            else:
                # numero_conta = int(ref_contas["0"]["numero_total_contas"]) + 1
                # titular = ref_clientes[cpf]["nome"]
                # nova_conta = {
                #     "cpf": cpf,
                #     "numero_conta": numero_conta,
                #     "titular": titular,
                # }
                meu_banco.registrar_conta(cpf)
                print("\nConta registrada com sucesso")

        elif opcao == "lu":
            meu_banco.listar_usuarios()

        elif opcao == "lc":
            meu_banco.listar_contas()

        elif opcao == "es":
            conta_informada = input("Informe o número da conta para exibir o saldo: ")
            if not meu_banco.verificar_conta(conta_informada):
                print("\nConta não encontrada")
                continue
            meu_banco.exibir_saldo(conta_informada)

        elif opcao == "du":
            cpf = input(
                "\nInforme o cpf do usuário ou x para voltar: "
            )
            if cpf.lower() == "x":
                continue
            elif not cpf.isdigit():
                print("\nDigite apenas números")
                continue
            elif not meu_banco.verificar_cpf(cpf):
                print("\nNão existe um usuário com este CPF")
                continue
            meu_banco.deletar_usuario(cpf)
            print("\nUsuário deletado com sucesso")

        elif opcao == "dc":
            conta_informada = input(
                "\nInforme o número da conta a deletar ou x para voltar: "
            )
            if conta_informada.lower() == "x":
                continue
            if not meu_banco.verificar_conta(conta_informada):
                print("Conta não encontrada")
                continue
            meu_banco.deletar_conta(conta_informada)
            print("\nConta deletada com sucesso")


        elif opcao == "x":
            print("Obrigado por utilizar nossos serviços.")
            break


main()
