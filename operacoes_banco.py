import datetime
import json
import os
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
        cpf = kwargs.get("cpf")
        args_nomeados = kwargs.copy()
        if "cpf" in args_nomeados:
            del args_nomeados["cpf"]
        try:
            with open(ROOT_PATH / "log.txt", "a", encoding="utf-8") as arquivo_log:
                if cpf:
                    arquivo_log.write(
                        f"{now.strftime('%d/%m/%Y %H:%M:%S')}, "
                        f"cliente de cpf {cpf}, "
                        f"fez a ação de {func.__name__} "
                        f"com os argumentos: [{args}, {args_nomeados}], "
                        f"e retornou {f} \n"
                    )
                else:
                    arquivo_log.write(
                        f"{now.strftime('%d/%m/%Y %H:%M:%S')}, "
                        f"Foi executada a ação de {func.__name__}\n"
                    )
        except Exception as exc:
            print(f"Erro ao tentar registrar a ação.\nErro:{exc}")
        return func.__name__

    return faz_log


def menu():
    return input(
        """\n=========== MENU DE OPERAÇÕES ===========\n
        escolha uma opção: \n
        [d] Depositar
        [s] Sacar
        [e] Extrato
        [ru] Registrar Usuário
        [rc] Registrar Conta
        [lu] Listar Usuários
        [lc] Listar Contas
        [es] Exibir Saldo
        [x] Sair
              \n========================================\n
    => """
    )

try:
    with open (ROOT_PATH / "clientes.json", "r", encoding="utf-8") as arquivo_clientes:
        ref_clientes = json.load(arquivo_clientes)
except:
    ref_clientes = {}

try:
    with open (ROOT_PATH / "contas.json", "r", encoding="utf-8") as arquivo_contas:
        ref_contas = json.load(arquivo_contas)
except:
    ref_contas = {"0":{"numero_total_contas": "0"}}


class Transacoes:
    def __init__(self, contas):
        self.contas = contas
    def depositar(self):
        pass
    def sacar(self):
        pass

class Banco:
    def __init__(self, clientes, contas):
        self.clientes = clientes
        self.contas = contas
        self.agencia = "0001"

    def registrar_usuario(self, novo_cliente):
        self.clientes[novo_cliente["cpf"]] = {
            "nome":novo_cliente["nome"],
            "data_nascimento":novo_cliente["data_nascimento"],
            "endereco":novo_cliente["endereco"],
            "contas": []
        }
        self.salvar_atualizacoes()
        print("\nUsuário registrado com sucesso")

    def registrar_conta(self, nova_conta):
        self.contas[nova_conta["numero_conta"]] = {
            "agencia": self.agencia,
            "saldo": 0,
            "limite_valor_saque_dia": 500,
            "saques_efetuados_hoje": 0,
            "titular": nova_conta["titular"],
            "cpf": nova_conta["cpf"],
            }
        numero_total_contas = nova_conta["numero_conta"]
        self.contas["0"]["numero_total_contas"] = str(numero_total_contas)
        self.clientes[nova_conta["cpf"]]["contas"].append({
            "agencia": self.agencia,
            "numero_conta": nova_conta["numero_conta"]
        })
        self.salvar_atualizacoes()
        print("\nConta registrada com sucesso")
        
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
                """)
        )

    def listar_usuarios(self):
        for cpf, usuario in self.clientes.items():
            print(textwrap.dedent(f"""
                nome: {usuario['nome']}
                cpf: {cpf}
                data de nascimento: {usuario['data_nascimento']}
                endereço: {usuario['endereco']}
                contas: 
            """))
            for conta in usuario['contas']:
                print(f"""
                agência: {conta['agencia']}
                numero da conta: {conta['numero_conta']}
                """)
            print("\n----------------------------------------\n")

    def exibir_saldo(self, conta_informada):
        print(f"O saldo da conta {conta_informada} é R$ {self.contas[conta_informada]['saldo']:.2f}")

    def salvar_atualizacoes(self):
        try:
            with open (ROOT_PATH / "clientes.json", "w", encoding="utf-8") as arquivo_clientes:
                json.dump(self.clientes, arquivo_clientes, indent=2)
        except IOError as exc:
            print(f"Erro ao tentar salvar as atualizações no arquivo de cliente: {exc}")

        try:
            with open (ROOT_PATH / "contas.json", "w", encoding="utf-8") as arquivo_contas:
                json.dump(self.contas, arquivo_contas, indent=2)
        except IOError as exc:
            print(f"Erro ao tentar salvar as atualizações no arquivo de contas: {exc}")
            




@decorador_log
def sacar_ou_depositar(conta_informada, valor, *, metodo, cpf):
    try:
        with (
            open(ROOT_PATH / "contas.jsonl", "r", encoding="utf-8") as leitura_contas,
            open(ROOT_PATH / "contas_temp.jsonl", "w", encoding="utf-8"
            ) as escrita_contas,
        ):
            for linha in leitura_contas:
                conta = json.loads(linha)
                if conta_informada == conta.get("numero_conta"):
                    if metodo == "saque":
                        if valor > conta["saldo"]:
                            print("Saldo insuficiente")
                        elif valor > conta["limite_valor_saque_dia"]:
                            print("Limite de valor diário excedido")
                        elif conta["saques_efetuados_hoje"] == 10:
                            print("Limite de saques diários excedido")
                        else:
                            conta["saldo"] -= valor
                            conta["saques_efetuados_hoje"] += 1
                            conta["limite_valor_saque_dia"] -= valor
                    elif metodo == "deposito":
                        conta["saldo"] += valor
                escrita_contas.write(json.dumps(conta) + "\n")
        os.replace(ROOT_PATH / "contas_temp.jsonl", ROOT_PATH / "contas.jsonl")
        print("Operação realizada com sucesso.")
    except IOError as exc:
        print(f"Erro ao realizar a operação. {exc}")
    except IsADirectoryError as exc:
        print(f"Erro ao tentar abrir o arquivo. {exc}")
    except FileNotFoundError as exc:
        print(f"Arquivo não encontrado. {exc}")
    except Exception as exc:
        print(f"Erro ao realizar a operação. {exc}")
    finally:
        if os.path.exists(ROOT_PATH / "contas_temp.jsonl"):
            arquivo_temp = ROOT_PATH / "contas_temp.jsonl"
            os.remove(arquivo_temp)
    if metodo == "sacar":
        return "Saque", valor
    elif metodo == "depositar":
        return "Depósito", valor


@decorador_log
def exibir_extrato(saldo, /, *, extrato, conta, tipo_operacao, cpf):

    def filtro_operacoes():
        for operacoes in extrato[conta]:
            if tipo_operacao == "d" and operacoes["tipo_operação"] == "Depósito":
                yield operacoes
            elif tipo_operacao == "s" and operacoes["tipo_operação"] == "Saque":
                yield operacoes
            elif tipo_operacao == "":
                yield operacoes

    op_filtradas = filtro_operacoes()
    print(
        f"""\n================ EXTRATO ================
            \nConta: {conta}"""
    )
    for operacao in op_filtradas:
        print(
            f"{operacao['data']} - {operacao['tipo_operação']}: R$ {operacao['valor']:.2f}"
        )
    print(
        f""" \nSaldo: R$ {saldo:.2f}
                \n========================================= """
    )


@decorador_log
def registrar_usuario(nome, data_nascimento, cpf, endereco):
    try:
        with open(
            ROOT_PATH / "clientes.jsonl", "a", encoding="utf-8"
        ) as arquivo_usuarios:
            usuario = {
                "cpf": cpf,
                "nome": nome,
                "data_nascimento": data_nascimento,
                "endereco": endereco,
                "contas": [],
            }
            arquivo_usuarios.write(json.dumps(usuario) + "\n")
            print("Usuário registrado com sucesso.")
    except IOError as exc:
        print(f"Erro ao realizar a operação. {exc}")
    except IsADirectoryError as exc:
        print(f"Erro ao tentar abrir o arquivo. {exc}")
    except FileNotFoundError as exc:
        print(f"Arquivo não encontrado. {exc}")
    except Exception as exc:
        print(f"Erro ao realizar a operação. {exc}")
    return usuario["nome"], usuario["cpf"]


@decorador_log
def registrar_conta(nome, cpf):
    NUMERO_AGENCIA = "0001"
    nova_conta = None
    try:
        with (
            open(ROOT_PATH / "contas.jsonl", "r", encoding="utf-8") as contas_leitura,
            open(ROOT_PATH / "contas_temp.jsonl", "w", encoding="utf-8") as contas_escrita
        ):
            numero_conta = 0
            numero_total_contas = json.loads(contas_leitura.readline())
            numero_conta = numero_total_contas["numero_total_contas"] = numero_total_contas["numero_total_contas"] + 1
            contas_escrita.write(json.dumps(numero_total_contas) + "\n")
            for linha in contas_leitura:
                conta = json.loads(linha)
                contas_escrita.write(json.dumps(conta) + "\n")
            nova_conta = {
                "agencia": NUMERO_AGENCIA,
                "numero_conta": numero_conta,
                "saldo": 0,
                "limite_valor_saque_dia": 500,
                "saques_efetuados_hoje": 0,
                "titular": nome,
                "cpf": cpf,
            }
            contas_escrita.write(json.dumps(nova_conta) + "\n")
            print(
                f"Conta {numero_conta} foi criado com sucesso para o/a cliente {nome}"
            )
        os.replace(ROOT_PATH / "contas_temp.jsonl", ROOT_PATH / "contas.jsonl")

        with open(ROOT_PATH / "clientes.jsonl", "r", encoding="utf-8") as clientes_leitura, open(ROOT_PATH / "clientes_temp.jsonl", "w", encoding="utf-8") as clientes_escrita:
            for linha in clientes_leitura:
                cliente = json.loads(linha)
                if cliente["cpf"] == cpf:
                    cliente["contas"].append({"agencia": nova_conta["agencia"], "numero_conta": nova_conta["numero_conta"]})
                clientes_escrita.write(json.dumps(cliente) + "\n")
        os.replace(ROOT_PATH / "clientes_temp.jsonl", ROOT_PATH / "clientes.jsonl")
            
    except IOError as exc:
        print(f"Erro ao realizar a operação. {exc}")
    except IsADirectoryError as exc:
        print(f"Erro ao tentar abrir o arquivo. {exc}")
    except FileNotFoundError as exc:
        print(f"Arquivo não encontrado. {exc}")
    except json.JSONDecodeError as exc:
        print(f"Erro ao processar os dados. {exc}")
    except PermissionError as exc:
        print(f"Permissão negada ao acessar o arquivo. {exc}")
    except Exception as exc:
        print(f"Erro ao realizar a operação. {exc}")
    return nova_conta["agencia"], nova_conta["numero_conta"], nova_conta["cpf"]


@decorador_log
def listar_contas():
    # for contas in ContaIterator(contas):
    try:
        with open(ROOT_PATH / "contas.jsonl", "r", encoding="utf-8") as arquivo_contas:
            next(arquivo_contas)
            for linha in arquivo_contas:
                conta = json.loads(linha)
                print(
                    textwrap.dedent(
                        f"""\n
                    Conta: {conta["numero_conta"]}\n
                    Agência: {conta["agencia"]}\n
                    Saldo: R$ {conta["saldo"]:.2f}\n
                    Limite disponível para saque hoje: R$ {conta["limite_valor_saque_dia"]:.2f}\n
                    Titular: {conta["titular"]}\n
                    CPF: {conta["cpf"]}\n\n\n"""
                    )
                )
    except IOError as exc:
        print(f"Erro ao realizar a operação. {exc}")
    except IsADirectoryError as exc:
        print(f"Erro ao tentar abrir o arquivo. {exc}")
    except FileNotFoundError as exc:
        print(f"Arquivo não encontrado. {exc}")
    except Exception as exc:
        print(f"Erro ao realizar a operação. {exc}")

    # ou podemos usar o iterador nativo do Python para iterar
    # sobre a lista de contas, já que as listas são iteráveis por padrão:

    # iterador = iter(contas)
    # for conta in iterador:
    # e o print


@decorador_log
def listar_usuarios():
    try:
        with open(
            ROOT_PATH / "clientes.jsonl", "r", encoding="utf-8"
        ) as arquivo_usuarios:
            for linha in arquivo_usuarios:
                usuario = json.loads(linha)
                print(
                    textwrap.dedent(
                        f"""\n
                    Nome: {usuario["nome"]}\n
                    cpf: {usuario["cpf"]}\n
                    Data de Nascimento: {usuario["data_nascimento"]}\n
                    Endereço: {usuario["endereco"]}\n
                    Contas:
                    """
                    )
                )
                contas = usuario.get("contas", [])
                for conta in contas:
                    print(
                        textwrap.dedent(
                            f"""
                        N° da conta: {conta["numero_conta"]}\n
                        Agência: {conta["agencia"]}\n\n"""
                        )
                    )
                print("\n----------------------------------------\n")
    except IOError as exc:
        print(f"Erro ao realizar a operação. {exc}")
    except IsADirectoryError as exc:
        print(f"Erro ao tentar abrir o arquivo. {exc}")
    except FileNotFoundError as exc:
        print(f"Arquivo não encontrado. {exc}")
    except Exception as exc:
        print(f"Erro ao realizar a operação. {exc}")


def main():
    meu_banco = Banco(ref_clientes, ref_contas)


    while True:
        opcao = menu().lower()
        if opcao == "d":
            conta_informada = int(input("Informe o número da conta para depósito: "))
            conta_encontrada = False
            arquivo_contas = open(ROOT_PATH / "contas.jsonl", "r", encoding="utf-8")
            for linha in arquivo_contas:
                conta = json.loads(linha)
                if conta_informada == conta.get("numero_conta"):
                    valor_str = input("Informe o valor do depósito ou digite x para voltar: ")
                    conta_encontrada = True
                    if valor_str.lower() == "x":
                        break
                    cpf = conta["cpf"]
                    arquivo_contas.close()
                    sacar_ou_depositar(
                        conta_informada, valor = float(valor_str), metodo="deposito", cpf = cpf
                        )
                    break
            if not conta_encontrada:
                print("\nConta não encontrada")

        elif opcao == "s":
            conta_informada = int(input("Informe o número da conta para saque: "))
            conta_encontrada = False
            arquivo_contas = open(ROOT_PATH / "contas.jsonl", "r", encoding="utf-8")
            for linha in arquivo_contas:
                conta = json.loads(linha)
                if conta_informada == conta.get("numero_conta"):
                    valor_str = input("Informe o valor para sacar ou digite x para voltar: ")
                    if valor_str.lower() == "x":
                        continue
                    conta_encontrada = True
                    cpf = conta["cpf"]
                    arquivo_contas.close()
                    sacar_ou_depositar(
                        conta_informada, valor = float(valor_str), metodo="saque", cpf = cpf
                        )
                    break
            if not conta_encontrada:
                print("\nConta não encontrada")

        elif opcao == "e":
            conta = int(input("Informe o número da conta para exibir o extrato: "))
            if conta not in [c["numero_conta"] for c in contas]:
                print("Conta não encontrada.")
                continue
            elif conta not in extrato:
                print("\nNão foram realizadas movimentações para essa conta.")
                continue
            else:
                saldo = next(c["saldo"] for c in contas if c["numero_conta"] == conta)
                # for c in contas:
                #     if c["numero_conta"] == conta:
                #         saldo = c["saldo"]
                tipo_operacao = input(
                    "\n\nDeseja filtrar o extrato por tipo de operação?\n\n (d) Depósitos\n (s) Saques\n"
                    "       Ou pressione Enter para exibir todos\n\n => "
                ).lower()
                exibir_extrato(
                    saldo, extrato=extrato, conta=conta, tipo_operacao=tipo_operacao
                )

        elif opcao == "ru":
            cpf = input("Informe o número do cpf ou x para voltar: ")
            if cpf.lower() == "x":
                continue
            if cpf in ref_clientes:
                print("Este CPF já está associado a um usuário")
                continue
            else:
                nome = input("Informe o nome do novo cliente: ")
                data_nascimento = input(
                    "Informe a data de nascimento do novo cliente (DD-MM-AAAA): "
                )
                endereco = input(
                    "Informe o endereço do novo cliente (logradouro, número - bairro - cidade/sigla estado): "
                )
                novo_cliente = {"cpf":cpf, "nome":nome, "data_nascimento": data_nascimento, "endereco": endereco}
                meu_banco.registrar_usuario(novo_cliente)

        elif opcao == "rc":
            cpf = input("\nInforme o cpf do usuário titular da nova conta ou x para voltar: ")
            if cpf.lower() == "x":
                continue
            if cpf not in ref_clientes:
                print("\nÉ necessário cadastrar o cliente antes de criar uma conta")
                continue
            else:
                numero_conta = int(ref_contas["0"]["numero_total_contas"]) + 1
                titular = ref_clientes[cpf]["nome"]
                nova_conta = {"cpf":cpf, "numero_conta": numero_conta, "titular": titular}
                meu_banco.registrar_conta(nova_conta)
                
        elif opcao == "lu":
            meu_banco.listar_usuarios()

        elif opcao == "lc":
            meu_banco.listar_contas()

        elif opcao == "es":
            conta_informada = input("Informe o número da conta para exibir o saldo: ")
            if conta_informada not in ref_contas:
                print("\nConta não encontrada")
                continue
            meu_banco.exibir_saldo(conta_informada)
            
        elif opcao == "x":
            print("Obrigado por utilizar nossos serviços.")
            break


main()
