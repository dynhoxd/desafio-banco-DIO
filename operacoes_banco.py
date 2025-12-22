import datetime
import textwrap
from pathlib import Path
ROOT_PATH = Path(__file__).parent


def decorador_log(func):
    def faz_log(*args, **kwargs):
        now = datetime.datetime.now()
        f = func(*args, **kwargs)
        try:
            with open(ROOT_PATH / "log.txt", "a", encoding="utf-8")\
                    as arquivo_log:
                arquivo_log.write(f'''{now.strftime("%d/%m/%Y %H:%M:%S")},
                                    a função {func.__name__}
                                    foi executada com os argumentos: [{args}, {kwargs}],
                                    e retornou {f} \n''')
        except Exception as exc:
            print(f"Erro ao tentar registrar a ação.\nErro:{exc}")
        return f
    return faz_log  

def menu():
    return input("""\n=========== MENU DE OPERAÇÕES ===========\n
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
    => """)

@decorador_log
def depositar(saldo, valor, extrato, conta, /):
    if valor > 0:
        now = datetime.datetime.now()
        saldo += valor
        movimento = {"tipo_operação": "Depósito", "valor": valor, "data": now.strftime("%d/%m/%Y %H:%M:%S")}
        extrato.setdefault(conta, []).append(movimento)
        print("Depósito realizado com sucesso.")
        print(f"Saldo atual: R$ {saldo:.2f}")
        # return saldo, extrato
    else:
        print("Operação falhou! O valor informado é inválido.")
        # return saldo, extrato
    return saldo, extrato

@decorador_log   
def sacar(*, saldo, valor, extrato, limite_diario, saques_efetuados_hoje, limite_saques_disponivel_dia, conta):
    voltar_menu = False
    if valor > saldo:
        print("Operação falhou! Não há saldo suficiente.")
    elif valor > limite_diario:
        print("Operação falhou! O valor do saque excede o limite diário.")
        voltar_menu = True
    elif saques_efetuados_hoje > limite_saques_disponivel_dia:
        print("Operação falhou! Número máximo de saques excedido.")
        voltar_menu = True
    elif valor > 0:
        now = datetime.datetime.now()
        saldo -= valor
        movimento = {"tipo_operação": "Saque", "valor": valor, "data": now.strftime("%d/%m/%Y %H:%M:%S")}
        extrato.setdefault(conta, []).append(movimento)
        saques_efetuados_hoje += 1
        limite_diario -= valor
        limite_saques_disponivel_dia -= 1
        print("Saque realizado com sucesso.")
        print(f"Saldo atual: R$ {saldo:.2f}")
        voltar_menu = True
    else:
        print("Operação falhou! O valor informado é inválido.")
    
    return saldo, extrato, saques_efetuados_hoje, limite_diario, limite_saques_disponivel_dia, voltar_menu

@decorador_log        
def exibir_extrato(saldo, /, *, extrato, conta, tipo_operacao):
    
    def filtro_operacoes():
        for operacoes in extrato[conta]:
            if tipo_operacao == 'd' and operacoes['tipo_operação'] == 'Depósito':
                yield operacoes
            elif tipo_operacao == 's' and operacoes['tipo_operação'] == 'Saque':
                yield operacoes
            elif tipo_operacao == '':
                yield operacoes
        
    op_filtradas = filtro_operacoes()
    print(f'''\n================ EXTRATO ================
            \nConta: {conta}''')
    for operacao in op_filtradas:
        print(f"{operacao['data']} - {operacao['tipo_operação']}: R$ {operacao['valor']:.2f}")
    print(f''' \nSaldo: R$ {saldo:.2f}
                \n========================================= ''')

@decorador_log
def registrar_usuario(nome, data_nascimento, cpf, endereco, usuarios):
    usuario = {"cpf":cpf, 
                "nome": nome,
                "data_nascimento": data_nascimento,
                "endereco": endereco,
                "contas": []
    }
    usuarios.append(usuario)
    print("\nUsuário registrado com sucesso.")
    return usuarios

@decorador_log
def registrar_conta(numero_agencia, numero_conta, usuario, contas, cpf):
    conta = {
            "agencia": numero_agencia,
            "numero_conta": numero_conta,
            'saldo': 0,
            "limite_valor_saque_dia": 500,
            "saques_efetuados_hoje": 0,
            "limite_saques_disponivel_dia": 10,
            "titular": usuario["nome"],
            "cpf": cpf}
    contas.append(conta)
    usuario["contas"].append(conta)
    print(f"\nA conta n° {numero_conta} da agência {numero_agencia} foi criada para o(a) cliente {usuario["nome"]}.")

@decorador_log
def listar_contas(contas):
    iterador = iter(contas)
    while True:
        try:
            conta = next(iterador)
            print(textwrap.dedent(f'''\n
                Conta: {conta["numero_conta"]}\n
                Agência: {conta["agencia"]}\n
                Saldo: R$ {conta["saldo"]:.2f}\n
                Limite disponível para saque hoje: R$ {conta["limite_valor_saque_dia"]:.2f}\n
                Titular: {conta["titular"]}\n
                CPF: {conta["cpf"]}\n\n\n'''))
        except StopIteration:
            break

@decorador_log
def listar_usuarios(usuarios):
        user_interator = iter(usuarios)
        while True:
            try:
                usuario = next(user_interator)
                print(textwrap.dedent(f'''\n
                Nome: {usuario["nome"]}\n
                cpf: {usuario["cpf"]}\n
                Data de Nascimento: {usuario["data_nascimento"]}\n
                Endereço: {usuario["endereco"]}\n
                Contas:
                '''))
                contas = usuario.get("contas", [])
                for conta in contas:
                    print(textwrap.dedent(f'''
                    N° da conta: {conta["numero_conta"]}\n
                    Agência: {conta["agencia"]}\n\n'''))
                print("\n----------------------------------------\n")
            except StopIteration:
                break

def main():
    extrato = {}
    contagem_contas = 2
    NUMERO_AGENCIA = "0001"
    usuarios = [{"cpf": "123",
                 "nome": "Ana Pereira",
                 "data_nascimento": "01-01-2000",
                 "endereco": "Rua A, 123 - Centro - Rio de Janeiro/RJ",
                 "contas":[{"agencia": '0001',
                            "numero_conta": 1,
                            "titular": "Ana",
                            "cpf": 123}]},
                 {"cpf": "234",
                  "nome": "Bruno Cardoso",
                  "data_nascimento": "02-02-1990",
                  "endereco": "Avenida B, 456 - Sé - São Paulo/SP",
                  "contas":[{"agencia": '0001',
                            "numero_conta": 2,
                            "titular": "Bruno",
                            "cpf": 234}]}]
    contas = [{"agencia": NUMERO_AGENCIA,
               "numero_conta": 1,
               "saldo": 1000,
               "limite_valor_saque_dia": 500,
               "saques_efetuados_hoje": 0,
               "limite_saques_disponivel_dia": 10,
               "titular": "Ana",
               "cpf": "123"},
               {"agencia": NUMERO_AGENCIA,
                "numero_conta": 2,
                "saldo": 300,
                "limite_valor_saque_dia": 500,
                "saques_efetuados_hoje": 0,
                "limite_saques_disponivel_dia": 10,
                "titular": "Bruno",
                "cpf": "234"}]

    while True:
        opcao = menu().lower()
        if opcao == "d":
            conta = int(input("Informe o número da conta para depósito: "))
            if conta not in [c["numero_conta"] for c in contas]:
                print("Conta não encontrada.")
                continue
            else:
                valor_str = input("Informe o valor do depósito ou digite x para voltar: ")
                if valor_str.lower() == "x":
                    continue
                for c in contas:
                    if c["numero_conta"] == conta:
                        saldo = c["saldo"]
                        valor = float(valor_str)
                        saldo, extrato = depositar(saldo, valor, extrato, conta)
                        c["saldo"] = saldo
        elif opcao == "s":
            while True:
                conta = int(input("Informe o número da conta para saque: "))
                s_iterator = iter(contas)
                while True:
                    try:
                        c = next(s_iterator)
                        if conta == c["numero_conta"]:
                            valor_str = input("Informe o valor do saque ou digite x para voltar: ").lower()
                            if valor_str == "x":
                                voltar_menu = True
                                break
                            saldo = c["saldo"]
                            limite_diario = c['limite_valor_saque_dia']
                            saques_efetuados_hoje = c['saques_efetuados_hoje']
                            limite_saques_disponivel_dia = c['limite_saques_disponivel_dia']
                            valor = float(valor_str)
                            saldo, extrato, saques_efetuados_hoje, limite_diario, limite_saques_disponivel_dia, voltar_menu = sacar(
                            saldo=saldo,
                            valor=valor,
                            extrato=extrato,
                            limite_diario=limite_diario,
                            saques_efetuados_hoje=saques_efetuados_hoje,
                            limite_saques_disponivel_dia=limite_saques_disponivel_dia,
                            conta=conta)
                            c["saldo"] = saldo
                            c["limite_saques_disponivel_dia"] = limite_saques_disponivel_dia
                            c["saques_efetuados_hoje"] = saques_efetuados_hoje
                            c["limite_valor_saque_dia"] = limite_diario
                            voltar_menu = True
                            break
                    except StopIteration:
                        print("Conta não encontrada.")
                        voltar_menu = True
                        break
                if voltar_menu:
                    break
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
                tipo_operacao = input("\n\nDeseja filtrar o extrato por tipo de operação?\n\n (d) Depósitos\n (s) Saques\n     Ou pressione Enter para exibir todos\n\n => ").lower()
                exibir_extrato(saldo, extrato=extrato, conta=conta, tipo_operacao=tipo_operacao)
        elif opcao == "ru":
            cpf = input("Informe o CPF do novo cliente (somente números): ")
            ru_user_iterator = iter(usuarios)
            while True:
                try:
                    usuario = next(ru_user_iterator)
                    if usuario.get("cpf") == cpf:
                        cpf_existe = True
                        break
                except StopIteration:
                    cpf_existe = False
                    break
            if cpf_existe:
                print("Já existe um usuário com esse CPF.")
            else:
                nome = input("Informe o nome do novo cliente: ")
                data_nascimento = input("Informe a data de nascimento do novo cliente (DD-MM-AAAA): ")
                endereco = input("Informe o endereço do novo cliente (logradouro, número - bairro - cidade/sigla estado): ")
                usuarios = registrar_usuario(nome, data_nascimento, cpf, endereco, usuarios)
        elif opcao == "rc":
            cpf = input("Informe o cpf do usuário titular da nova conta: ")
            rc_user_iterator = iter(usuarios)
            while True:
                try:
                    usuario = next(rc_user_iterator)
                    if usuario.get("cpf") == cpf:
                        contagem_contas += 1
                        numero_conta = contagem_contas
                        registrar_conta(NUMERO_AGENCIA, numero_conta, usuario, contas, cpf)
                        break
                except StopIteration:
                    print("Usuário não encontrado. Por favor, registre o usuário antes de criar uma conta!")
                    break
        elif opcao == "lu":
            listar_usuarios(usuarios)
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "x":
            print("Obrigado por utilizar nossos serviços.")
            break    
main()


# menu = """

# [d] Depositar
# [s] Sacar
# [e] Extrato
# [q] Sair

# => """

# saldo = 0
# limite = 500
# extrato = ""
# saques_efetuados_hoje = 0
# limite_saques_disponivel_dia = 3

# while True:

#     opcao = input(menu)

#     if opcao == "d":
#         valor = float(input("Informe o valor do depósito: "))

#         if valor > 0:
#             saldo += valor
#             extrato += f"Depósito: R$ {valor:.2f}\n"

#         else:
#             print("Operação falhou! O valor informado é inválido.")

#     elif opcao == "s":
#         valor = float(input("Informe o valor do saque: "))

#         excedeu_saldo = valor > saldo

#         excedeu_limite = valor > limite

#         excedeu_saques = saques_efetuados_hoje >= limite_saques_disponivel_dia

#         if excedeu_saldo:
#             print("Operação falhou! Você não tem saldo suficiente.")

#         elif excedeu_limite:
#             print("Operação falhou! O valor do saque excede o limite.")

#         elif excedeu_saques:
#             print("Operação falhou! Número máximo de saques excedido.")

#         elif valor > 0:
#             saldo -= valor
#             extrato += f"Saque: R$ {valor:.2f}\n"
#             saques_efetuados_hoje += 1

#         else:
#             print("Operação falhou! O valor informado é inválido.")

#     elif opcao == "e":
#         print("\n================ EXTRATO ================")
#         print("Não foram realizadas movimentações." if not extrato else extrato)
#         print(f"\nSaldo: R$ {saldo:.2f}")
#         print("==========================================")

#     elif opcao == "q":
#         break

#     else:
#         print("Operação inválida, por favor selecione novamente a operação desejada.")
