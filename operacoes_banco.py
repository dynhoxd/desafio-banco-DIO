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

#         excedeu_saques = numero_saques > LIMITE_SAQUES

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






def menu():
    return input("""\n========= MENU DE OPERAÇÕES =========\n
        escolha uma opção: \n
        [d] Depositar
        [s] Sacar
        [e] Extrato
        [cu] Criar Usuário
        [cc] Criar Conta
        [lc] Listar Contas
        [x] Sair
              \n=====================================\n
            => """)

def depositar(saldo, valor, extrato, /):
    if valor > 0:
        saldo += valor
        extrato += f"Depósito: R$ {valor:.2f}\n"
        print("Depósito realizado com sucesso.")
        print(f"Saldo atual: R$ {saldo:.2f}")
        return saldo, extrato
    else:
        print("Operação falhou! O valor informado é inválido.")
        return saldo, extrato
    
def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    sucesso = False
    if valor > saldo:
        print("Operação falhou! Não há saldo suficiente.")
    elif valor > limite:
        print("Operação falhou! O valor do saque excede o limite diário.")
    elif numero_saques > limite_saques:
        print("Operação falhou! Número máximo de saques excedido.")
    elif valor > 0:
        saldo -= valor
        extrato += f"Saque: R$ {valor:.2f}\n"
        numero_saques += 1
        limite -= valor
        limite_saques -= 1
        print("Saque realizado com sucesso.")
        print(f"Saldo atual: R$ {saldo:.2f}")
        sucesso = True
    else:
        print("Operação falhou! O valor informado é inválido.")
    
    return saldo, extrato, numero_saques, limite, limite_saques, sucesso
        
def exibir_extrato(saldo, /, extrato): 
    print("\n================ EXTRATO ================")
    if not extrato:
        print("Não foram realizadas movimentações.")
    else:
        print(extrato)
    print(f"\nSaldo: R$ {saldo:.2f}")
    print("==========================================")

def main():
    saldo = 0
    limite = 500
    extrato = ""
    numero_saques = 0
    LIMITE_SAQUES = 3
    usuários = {}
    contas = {}

    while True:
        opcao = menu()
        if opcao == "d":
            valor = float(input("Informe o valor do depósito: "))
            saldo, extrato = depositar(saldo, valor, extrato)
        elif opcao == "s":
            while True:
                valor = float(input("Informe o valor do saque: "))
                saldo, extrato, numero_saques, limite, LIMITE_SAQUES, sucesso = sacar(
                    saldo=saldo,
                    valor=valor,
                    extrato=extrato,
                    limite=limite,
                    numero_saques=numero_saques,
                    limite_saques=LIMITE_SAQUES,
                )
                if sucesso:
                    break
        elif opcao == "e":
            exibir_extrato(saldo, extrato)
        elif opcao == "x":
            print("Obrigado por utilizar nossos serviços.")
            break    
main()







# def criar_usuario(usuarios):
# def criar_conta(agencia, numero_conta, usuarios):
# def listar_contas(contas):

