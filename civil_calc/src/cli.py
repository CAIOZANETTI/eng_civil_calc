
import json
import sys
from civil_calc.nucleo import orquestrador

def main() -> None:
    if len(sys.argv) != 3:
        print("uso: cli.py <modulo> '<json>'")
        sys.exit(1)
    modulo = sys.argv[1]
    entradas = json.loads(sys.argv[2])
    df = orquestrador.executar(modulo, entradas)
    print(df)

if __name__ == "__main__":
    main()
