# import datetime
# now = datetime.datetime.now()

# def decorador_log(func): 
#     return print(f'{now.strftime("%d/%m/%Y %H:%M:%S")} - a ação de {func.__name__} é executada.')

def menu():
    return input("""\n========= MENU DE OPERAÇÕES =========\n
        escolha uma opção: \n
        [d] Depositar
        [s] Sacar
        [e] Extrato
        [ru] Registrar Usuário
        [cc] Criar Conta
        [lu] Listar Usuários
        [lc] Listar Contas
        [x] Sair
              \n=====================================\n
            => """)

# @decorador_log
def depositar(saldo, valor, extrato, conta, /):
    if valor > 0:
        saldo += valor
        movimento = {"tipo_operação": "Depósito", "valor": valor, "data": now.strftime("%d/%m/%Y %H:%M:%S")}
        extrato.setdefault(conta, []).append(movimento)
        print("Depósito realizado com sucesso.")
        print(f"Saldo atual: R$ {saldo:.2f}")
        return saldo, extrato
    else:
        print("Operação falhou! O valor informado é inválido.")
        return saldo, extrato
    
def sacar(*, saldo, valor, extrato, limite_diario, numero_saques, limite_saques, conta):
    sucesso = False
    if valor > saldo:
        print("Operação falhou! Não há saldo suficiente.")
    elif valor > limite_diario:
        print("Operação falhou! O valor do saque excede o limite diário.")
    elif numero_saques > limite_saques:
        print("Operação falhou! Número máximo de saques excedido.")
    elif valor > 0:
        saldo -= valor
        movimento = {"tipo_operação": "Depósito", "valor": valor, "data": now.strftime("%d/%m/%Y %H:%M:%S")}
        extrato.setdefault(conta, []).append(movimento)
        numero_saques += 1
        limite_diario -= valor
        limite_saques -= 1
        print("Saque realizado com sucesso.")
        print(f"Saldo atual: R$ {saldo:.2f}")
        sucesso = True
    else:
        print("Operação falhou! O valor informado é inválido.")
    
    return saldo, extrato, numero_saques, limite_diario, limite_saques, sucesso, conta
        
def exibir_extrato(saldo, /, *, extrato, conta): 
    print(f'''\n================ EXTRATO ================
          \nConta: {conta}''')
    
    if not extrato:
        print("Não foram realizadas movimentações.")
    else:
        dados = extrato[conta]
        for movimento in dados:
            print(f"{movimento['data']} - {movimento['tipo_operação']}: R$ {movimento['valor']:.2f}")

    print(f"\nSaldo: R$ {saldo:.2f}")
    print("=========================================")

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

def criar_conta(numero_agencia, numero_conta, usuario, contas, cpf):
    conta = {
            "agencia": numero_agencia,
             "numero_conta": numero_conta,
             'saldo': 0,
             "titular": usuario["nome"],
             "cpf": cpf}
    contas.append(conta)
    usuario["contas"].append(conta)
    print("\nConta criada com sucesso.")

def listar_contas(contas):
    for conta in contas:
        limite_conta = conta['limite_valor_saque_dia']
        if limite_conta > conta['saldo']:
            limite_conta = conta['saldo']
        print(conta['limite_saques'], conta['numero_saques'])
        print(f'''\n
            Conta: {conta["numero_conta"]}\n
            Agência: {conta["agencia"]}\n
            Saldo: R$ {conta["saldo"]:.2f}\n
            Limite disponível para saque hoje: R$ {limite_conta:.2f}\n
            Titular: {conta["titular"]}\n
            CPF: {conta["cpf"]}\n\n\n''')

def listar_usuarios(usuarios):
    for usuario in usuarios:
        contas = usuario.get("contas", [])
        print(f'''\n
            Nome: {usuario["nome"]}\n
            cpf: {usuario["cpf"]}\n
            Data de Nascimento: {usuario["data_nascimento"]}\n
            Endereço: {usuario["endereco"]}\n
            Contas:
            ''')
        for conta in contas:
            print(f'''
                Conta: {conta["numero_conta"]}\n
                Agência: {conta["agencia"]}\n\n''')


def main():
    extrato = {}
    NUMERO_AGENCIA = "0001"
    usuarios = [{"cpf": 123,
                 "nome": "Ana",
                 "data_nascimento": "01-01-2000",
                 "endereco": "Rua A, 123 - Centro - Rio de Janeiro/RJ",
                 "contas":[{"agencia": '0001',
                            "numero_conta": 1,
                            "titular": "Ana",
                            "cpf": 123}]},
                 {"cpf": 234,
                  "nome": "Bruno",
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
               "numero_saques": 0,
               "limite_saques": 10,
               "titular": "Ana",
               "cpf": 123},
               {"agencia": NUMERO_AGENCIA,
                "numero_conta": 2,
                "saldo": 300,
                "limite_valor_saque_dia": 500,
                "numero_saques": 0,
                "limite_saques": 10,
                "titular": "Bruno",
                "cpf": 234}]

    while True:
        opcao = menu()
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
                        print(saldo)
                        valor = float(valor_str)
                        saldo, extrato = depositar(saldo, valor, extrato, conta)
                        c["saldo"] = saldo
        elif opcao == "s":
            while True:
                conta = int(input("Informe o número da conta para saque: "))
                if conta not in [c["numero_conta"] for c in contas]:
                    print("Conta não encontrada.")
                    continue
                for c in contas:
                    if c["numero_conta"] == conta:
                        saldo = c["saldo"]
                        limite_diario = c['limite_valor_saque_dia']
                        numero_saques = c['numero_saques']
                        limite_saques = c['limite_saques']
                        valor_str = input("Informe o valor do saque ou digite x para voltar: ")
                        if valor_str.lower() == "x":
                            sucesso = True
                            break
                        valor = float(valor_str)
                        saldo, extrato, numero_saques, limite_diario, limite_saques, sucesso, conta = sacar(
                        saldo=saldo,
                        valor=valor,
                        extrato=extrato,
                        limite_diario=limite_diario,
                        numero_saques=numero_saques,
                        limite_saques=limite_saques,
                        conta=conta
                        )
                        print(sucesso)
                        for c in contas:
                            if c["numero_conta"] == conta:
                                c["saldo"] = saldo
                                c["limite_saques"] = limite_saques
                                c["numero_saques"] = numero_saques
                if sucesso:
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
                exibir_extrato(saldo, extrato=extrato, conta=conta)
        elif opcao == "ru":
            cpf = int(input("Informe o CPF do novo cliente (somente números): "))
            cpf_existe = any(usuario.get("cpf") == cpf for usuario in usuarios)
            if cpf_existe:
                print("Já existe um usuário com esse CPF.")
            else:
                nome = input("Informe o nome do novo cliente: ")
                data_nascimento = input("Informe a data de nascimento do novo cliente (DD-MM-AAAA): ")
                endereco = input("Informe o endereço do novo cliente (logradouro, número - bairro - cidade/sigla estado): ")
                usuarios = registrar_usuario(nome, data_nascimento, cpf, endereco, usuarios)
        elif opcao == "cc":
            cpf = int(input("Informe o cpf do usuário titular da nova conta: "))
            for cliente in usuarios:
                if cliente.get("cpf") == cpf:
                    usuario = cliente
                    numero_conta = len(contas) + 1
                    criar_conta(NUMERO_AGENCIA, numero_conta, usuario, contas, cpf)
                    break
            else:
                print("Usuário não encontrado, por favor registre o usuário antes de criar uma conta.")
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
# numero_saques = 0
# LIMITE_SAQUES = 3

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

#         excedeu_saques = numero_saques >= LIMITE_SAQUES

#         if excedeu_saldo:
#             print("Operação falhou! Você não tem saldo suficiente.")

#         elif excedeu_limite:
#             print("Operação falhou! O valor do saque excede o limite.")

#         elif excedeu_saques:
#             print("Operação falhou! Número máximo de saques excedido.")

#         elif valor > 0:
#             saldo -= valor
#             extrato += f"Saque: R$ {valor:.2f}\n"
#             numero_saques += 1

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
