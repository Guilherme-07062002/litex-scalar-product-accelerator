#!/bin/bash
# Script de construção para compilar e executar os testbenches

# Obter o diretório atual e o diretório base do projeto
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_DIR=$(dirname "$SCRIPT_DIR")

# Definir diretórios usando caminhos absolutos
RTL_DIR="$PROJECT_DIR/rtl"
TB_DIR="$PROJECT_DIR/tb"
SIM_DIR="$PROJECT_DIR/sim"

# Cria diretório de saída se não existir
mkdir -p "$SIM_DIR"

# Função para compilar e executar um testbench específico
compile_and_run() {
    local name=$1
    shift  # Remove o primeiro argumento (nome)
    local tb_file=${!#}  # Último argumento é o testbench
    # Remove o último argumento (testbench)
    set -- "${@:1:$(($#-1))}"
    
    echo "=== Compilando $name ==="
    
    # Comando completo para debug
    echo "iverilog -g2012 -o \"$SIM_DIR/${name}.vvp\" $* \"$tb_file\""
    
    # Executar a compilação
    iverilog -g2012 -o "$SIM_DIR/${name}.vvp" "$@" "$tb_file"
    
    local result=$?
    if [ $result -eq 0 ]; then
        echo "=== Executando $name ==="
        # Executa a simulação a partir de tb/ para que $dumpfile("../sim/...\") gere VCDs em sim/
        ( cd "$TB_DIR" && vvp "../sim/${name}.vvp" )
    else
        echo "Erro na compilação de $name (código: $result)"
    fi
    echo
}

# Menu reduzido: apenas acelerador e GTKWave
show_main_menu() {
    echo "===== MENU DE TESTES ====="
    echo "1. Produto Escalar (Acelerador)"
    echo "2. Visualizar ondas (GTKWave)"
    echo "3. Sair"
    echo "============================="
    echo -n "Escolha uma opção: "
}

# Função para abrir um VCD no GTKWave (se existir)
open_vcd() {
    local vcd_file="$SIM_DIR/$1"
    if [ -f "$vcd_file" ]; then
        if command -v gtkwave >/dev/null 2>&1; then
            echo "Abrindo $vcd_file no GTKWave..."
            gtkwave "$vcd_file" &
        else
            echo "GTKWave não encontrado no PATH. Instale o GTKWave e tente novamente."
            echo "Baixe em: http://gtkwave.sourceforge.net/"
        fi
    else
        echo "Arquivo não encontrado: $vcd_file"
        echo "Gerando automaticamente o VCD correspondente..."
        case $1 in
            "dot_product_accel.vcd")
                compile_and_run "dot_product_accel" "$RTL_DIR/dot_product_accel.sv" "$TB_DIR/tb_dot_product_accel.sv" ;;
            *)
                echo "Não foi possível identificar o teste para $1" ;;
        esac
        if [ -f "$vcd_file" ]; then
            echo "Abrindo $vcd_file no GTKWave..."
            gtkwave "$vcd_file" &
        else
            echo "Falha ao gerar o VCD: $vcd_file"
        fi
        read -r -p "Pressione ENTER para continuar..."
    fi
}

# Submenu para visualização de ondas
show_gtkwave_menu() {
    while true; do
        clear
        echo "===== VISUALIZAR ONDAS (GTKWave) ====="
        echo "1. Produto Escalar (dot_product_accel.vcd)"
        echo "2. Voltar"
        echo "======================================"
        echo -n "Escolha uma opção: "
        read -r opt
        case $opt in
            1) open_vcd "dot_product_accel.vcd" ;;
            2) break ;;
            *) echo "Opção inválida!"; read -r -p "Pressione ENTER para continuar..." ;;
        esac
    done
}

# Loop principal do menu
while true; do
    clear
    show_main_menu
    read -r main_option
    case $main_option in
        1)
            while true; do
                echo "===== TESTES PARA PRODUTO ESCALAR (ACELERADOR) ====="
                echo "1. Executar Testbench Completo"
                echo "2. Voltar"
                echo "============================================"
                read -r sub_option
                if [ "$sub_option" == "2" ]; then break; fi
                if [ "$sub_option" == "1" ]; then
                    compile_and_run "dot_product_accel" "$RTL_DIR/dot_product_accel.sv" "$TB_DIR/tb_dot_product_accel.sv"
                    echo "Pressione ENTER para continuar..."; read -r
                else
                    echo "Opção inválida!"; read -r
                fi
            done
            ;;
        2)
            show_gtkwave_menu
            ;;
        3)
            echo "Saindo do programa..."; exit 0
            ;;
        *)
            echo "Opção inválida! Pressione ENTER para continuar..."; read -r
            ;;
    esac
done
