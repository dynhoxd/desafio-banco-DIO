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
        try:
            with open(ROOT_PATH / "log.txt", "a", encoding="utf-8") as arquivo_log:
                arquivo_log.write(
                    f"{now.strftime('%d/%m/%Y %H:%M:%S')}, "
                    f"a função {func.__name__} "
                    f"foi executada com os argumentos: [{args}, {kwargs}], "
                    f"e retornou {f} \n"
                )
        except Exception as exc:
            print(f"Erro ao tentar registrar a ação.\nErro:{exc}")
        return f

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
        [x] Sair
              \n========================================\n
    => """
    )


@decorador_log
def sacar_e_depositar(conta_informada, valor_str, *, metodo):
    try:
        with (
            open(ROOT_PATH / "contas.jsonl", "r", encoding="utf-8") as leitura_contas,
            open(
                ROOT_PATH / "contas_temp.jsonl", "w", encoding="utf-8"
            ) as escrita_contas,
        ):
            for linha in leitura_contas:
                conta = json.loads(linha)
                if conta_informada == conta["numero_conta"]:
                    if metodo == "sacar":
                        conta["saldo"] -= float(valor_str)
                    elif metodo == "depositar":
                        conta["saldo"] += float(valor_str)
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


@decorador_log
def exibir_extrato(saldo, /, *, extrato, conta, tipo_operacao):

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
                "limite_saques_disponiveis_dia": 10,
                "Titular": nome,
                "cpf": cpf,
            }
            contas_escrita.write(json.dumps(nova_conta) + "\n")
            print(
                f"Conta {numero_conta} foi criado com sucesso para o/a cliente {nome}"
            )
        os.replace(ROOT_PATH / "contas_temp.jsonl", ROOT_PATH / "contas.jsonl")

        with (
            open(ROOT_PATH / "clientes.jsonl", "r", encoding="utf-8") as clientes_leitura,
            open(ROOT_PATH / "clientes_temp.jsonl", "w", encoding="utf-8") as clientes_escrita
        ):
            for linha in clientes_leitura:
                cliente = json.loads(linha)
                if cliente["cpf"] == cpf:
                    cliente["contas"].append({"agencia": nova_conta["agencia"], "numero_conta": nova_conta["numero_conta"]})
                clientes_escrita.write(json.dumps(cliente) + "\n")
        os.replace("C:\\Users\\jande\\Documents\\python\\desafio-banco\\clientes_temp.jsonl", "C:\\Users\\jande\\Documents\\python\\desafio-banco\\clientes.jsonl")
            
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

    # conta = {
    #     "agencia": numero_agencia,
    #     "numero_conta": numero_conta,
    #     "saldo": 0,
    #     "limite_valor_saque_dia": 500,
    #     "saques_efetuados_hoje": 0,
    #     "limite_saques_disponivel_dia": 10,
    #     "titular": usuario["nome"],
    #     "cpf": cpf,
    # }
    # contas.append(conta)
    # usuario["contas"].append(conta)
    # print(
    #     f"\nA conta n° {numero_conta} da agência {numero_agencia}"
    #     f" foi criada para o(a) cliente {usuario['nome']}."
    # )


@decorador_log
def listar_contas():
    # for contas in ContaIterator(contas):
    try:
        with open(ROOT_PATH / "contas.jsonl", "r", encoding="utf-8") as arquivo_contas:
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
    contagem_contas = 2
    NUMERO_AGENCIA = "0001"

    while True:
        opcao = menu().lower()
        if opcao == "d":
            conta_informada = int(input("Informe o número da conta para depósito: "))
            with open(
                ROOT_PATH / "contas.jsonl", "r", encoding="utf-8"
            ) as arquivo_contas:
                conta = [json.loads(linha) for linha in arquivo_contas]
                if conta_informada not in [c["numero_conta"] for c in conta]:
                    print("Conta não encontrada.")
                    continue
            valor_str = input("Informe o valor do depósito ou digite x para voltar: ")
            if valor_str.lower() == "x":
                continue
            sacar_e_depositar(conta_informada, valor_str, metodo="depositar")
        elif opcao == "s":
            conta_informada = int(input("Informe o número da conta para saque: "))
            with open(
                ROOT_PATH / "contas.jsonl", "r", encoding="utf-8"
            ) as arquivo_contas:
                conta = [json.loads(linha) for linha in arquivo_contas]
                if conta_informada not in [c["numero_conta"] for c in conta]:
                    print("Conta não encontrada.")
                    continue
            valor_str = input("Informe o valor do saque ou digite x para voltar: ")
            if valor_str.lower() == "x":
                continue
            sacar_e_depositar(conta_informada, valor_str, metodo="sacar")
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
            try:
                cpf = input("Informe o CPF do novo cliente (somente números): ")
                with open(
                    ROOT_PATH / "clientes.jsonl", "r", encoding="utf-8"
                ) as arquivo_usuarios:
                    for linha in arquivo_usuarios:
                        usuario = json.loads(linha)
                        if usuario.get("cpf") == cpf:
                            print("Usuário já cadastrado com esse CPF.")
                            break
                nome = input("Informe o nome do novo cliente: ")
                data_nascimento = input(
                    "Informe a data de nascimento do novo cliente (DD-MM-AAAA): "
                )
                endereco = input(
                    "Informe o endereço do novo cliente (logradouro, número - bairro - cidade/sigla estado): "
                )
                registrar_usuario(nome, data_nascimento, cpf, endereco)
            except IOError as exc:
                print(f"Erro ao realizar a operação. {exc}")
            except IsADirectoryError as exc:
                print(f"Erro ao tentar abrir o arquivo. {exc}")
            except FileNotFoundError as exc:
                print(f"Arquivo não encontrado. {exc}")
            except Exception as exc:
                print(f"Erro ao realizar a operação. {exc}")
        elif opcao == "rc":
            try:
                cpf = input("Informe o CPF do cliente: ")
                with open(
                    ROOT_PATH / "clientes.jsonl", "r", encoding="utf-8"
                ) as arquivo_usuarios:
                    encontrado = False
                    for linha in arquivo_usuarios:
                        usuario = json.loads(linha)
                        if usuario.get("cpf") == cpf:
                            nome = usuario["nome"]
                            registrar_conta(nome, cpf)
                            encontrado = True
                            break
                    if not encontrado:
                        print(
                            """Usuário não encontrado.
                            Por favor, registre o usuário antes de criar uma conta!"""
                        )
            except IOError as exc:
                print(f"Erro ao realizar a operação. {exc}")
            except IsADirectoryError as exc:
                print(f"Erro ao tentar abrir o arquivo. {exc}")
            except FileNotFoundError as exc:
                print(f"Arquivo não encontrado. {exc}")
            except Exception as exc:
                print(f"Erro ao realizar a operação. {exc}")

            # cpf = input("Informe o cpf do usuário titular da nova conta: ")
            # rc_user_iterator = iter(usuarios)
            # for usuario in rc_user_iterator:
            #     if usuario.get("cpf") == cpf:
            #         contagem_contas += 1
            #         numero_conta = contagem_contas
            #         registrar_conta(
            #             NUMERO_AGENCIA, numero_conta, usuario, contas, cpf
            #         )
            #         break
            # else:
            #     print(
            #         "Usuário não encontrado. Por favor, registre o usuário antes de criar uma conta!"
            #     )
        elif opcao == "lu":
            listar_usuarios()
        elif opcao == "lc":
            listar_contas()
        elif opcao == "x":
            print("Obrigado por utilizar nossos serviços.")
            break


main()
