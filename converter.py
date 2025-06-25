import re
import sys

def print_help():
    print("Usage: python converter.py --in=INPUT_FILE_NAME --out=OUTPUT_FILE_NAME")
    print("The arguments --in and --out are mandatory")
    print("The formats are detected by the extensions")
    print("The extensions are:\n\tMsolve .ms")
    print("\thpXbred and XL .in\n\tMagma .magma\n\tSage .sobj")
    print("\tSAT Solvers .sat")

def parse_args():
    params = {}
    args = sys.argv[1:]

    for arg in args:
        try:
            if arg[:2] == "--" and "=" in arg:
                key, value = arg[2:].split("=", 1)
                params[key] = value
            else:
                print("Invalid argument")
                print_help()
                sys.exit()
        except ValueError:
            print("Parsing error for the parameters")
            print_help()
            sys.exit()

    expected_keys = {"in", "out"}
    received_keys = set(params.keys())

    if received_keys != expected_keys:
        missing = expected_keys - received_keys
        extra = received_keys - expected_keys

        if missing:
            print(f"Missing parameters: {', '.join(missing)}")
        if extra:
            print(f"Not recongnized parameters: {', '.join(extra)}")
        print()
        print_help()
        sys.exit()

    return (params["in"], params["out"])

def check_formats(in_f, out_f):
    accepted_formats = ["ms", "in", "magma", "sobj", "sat"]
    try:
        _, format_in = in_f.split(".", 1)
        if format_in not in accepted_formats:
            print(f"format {format_in} is not supported")
            print_help()
            sys.exit()
        _, format_out = out_f.split(".", 1)
        if format_out not in accepted_formats:
            print(f"format {format_out} is not supported")
            print_help()
            sys.exit()
        return (format_in, format_out)
    except ValueError:
        print("Parsing error for the parameters")
        print_help()
        sys.exit()


if __name__ == "__main__":
    in_f, out_f = parse_args()
    format_in, format_out = check_formats(in_f, out_f)
    print(in_f, out_f)
    print(format_out, format_in)
