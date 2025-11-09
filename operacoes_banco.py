def menu():
    return input("""\n========= MENU DE OPERAÇÕES =========\n
        escolha uma opção: \n
        [d] Depositar
        [s] Sacar
        [e] Extrato
        [ru] Registrar Usuário
        [mu] Mostrar Usuários
        [cc] Criar Conta
        [lc] Listar Contas
        [lu] Listar Usuários
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
        
def exibir_extrato(saldo, /, *, extrato): 
    print("\n================ EXTRATO ================")
    if not extrato:
        print("Não foram realizadas movimentações.")
    else:
        print(extrato)
    print(f"\nSaldo: R$ {saldo:.2f}")
    print("=========================================")

def registrar_usuario(nome, data_nascimento, cpf, endereco, usuarios):
    usuario = {"cpf":cpf, 
                "nome": nome,
                "data_nascimento": data_nascimento,
                "endereco": endereco
    }
    usuarios.append(usuario)
    print("Usuário registrado com sucesso.")
    return usuarios

def criar_conta(numero_agencia, numero_conta, titular, contas):
    conta = {
            "agencia": numero_agencia,
             "numero_conta": numero_conta,
             "titular": titular}
    contas.append(conta)
    print("Conta criada com sucesso.")

def listar_contas(contas):
    for conta in contas:
        print(f"{conta}\n")

def listar_usuarios(usuarios):
    for usuario in usuarios:
        print(f"{usuario}\n")

def main():
    saldo = 0
    limite = 500
    extrato = ""
    numero_saques = 0
    LIMITE_SAQUES = 3
    NUMERO_AGENCIA = "0001"
    usuarios = [{"cpf": 123,
                 "nome": "Ana",
                 "data_nascimento": "01-01-2000",
                 "endereco": "Rua A, 123 - Centro - Rio de Janeiro/RJ"}]
    contas = []

    while True:
        opcao = menu()
        if opcao == "d":
            valor = float(input("Informe o valor do depósito: "))
            saldo, extrato = depositar(saldo, valor, extrato)
        elif opcao == "s":
            while True:
                valor_str = input("Informe o valor do saque ou digite x para voltar: ")
                if valor_str.lower() == "x":
                    break
                valor = float(valor_str)
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
            exibir_extrato(saldo, extrato=extrato)
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
            titular = input("Informe o nome do usuário titular da nova conta: ")
            numero_conta = len(contas) + 1
            criar_conta(NUMERO_AGENCIA, numero_conta, titular, contas)
        elif opcao == "lu":
            listar_usuarios(usuarios)
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "x":
            print("Obrigado por utilizar nossos serviços.")
            break    
main()