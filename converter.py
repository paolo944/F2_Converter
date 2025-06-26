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

def read_msolve(f):
    system = []
    variables = []
    try:
        with open(f, "r") as fd:
            lines = fd.readlines()
            variables = lines[0].replace("\n", "").split(",")
            if lines[1] != "2\n":
                print("File format .ms not correct. It has to be in charactarestic 2")
                sys.exit()
            
            for line in lines[2:]:
                poly = line.replace("\n", "").replace(",", "").split("+")
                system.append(poly)

        return (system, variables)
    except FileNotFoundError:
        print(f"File {f} not found")
        sys.exit()
    
def read_hpXbred(f):
    system = []
    variables = []
    try:
        with open(f, "r") as fd:
            lines = fd.readlines()
            variables = lines[0].replace("\n", "").split(",")

            for line in lines[1:]:
                if line[0] == "#":
                    continue
                poly = line.replace("\n", "").split("+")
                system.append(poly)
        return (system, variables)
    except FileNotFoundError:
        print(f"File {f} not found")
        sys.exit()

# F := GaloisField(2);
# Field<x1,x2,y1,y2> := BooleanPolynomialRing(4, "grevlex");
# f1 := x1+x2;
# f2 := x1+x2;
# f3 := x2*y1+x1*y2+x2+y1+1;
# f4 := x2*y1+x1*y2+y1+y2;
# f5 := x1+x2+y2+1;
# PolynomialSystem := [f1,f2,f3,f4,f5];

def read_magma(f):
    system = []
    variables = []
    try:
        with open(f, "r") as fd:
            lines = fd.readlines()
            if ":=GaloisField(2);\n" != lines[0].replace(" ", "")[1:] or "BooleanPolynomialRing" not in lines[1]:
                print("File format .magma not correct on the first line.")
            variables = re.findall(r'<(.*?)>', lines[1])[0].split(",")
            
            for line in lines[2:-1]:
                match = re.search(r':=\s*(.*?)(?:;|$)', line)

                if match:
                    expression = match.group(1).strip()
                    system.append(expression.split('+'))

        return (system, variables)
    except FileNotFoundError:
        print(f"File {f} not found")
        sys.exit()

def read_sage(f):
    system = []
    variables = []
    try:
        with open(f, "r") as fd:
            print()
        return (system, variables)
    except FileNotFoundError:
        print(f"File {f} not found")
        sys.exit()

def read_sat(f):
    system = []
    variables = []
    try:
        with open(f, "r") as fd:
            print()
        return (system, variables)
    except FileNotFoundError:
        print(f"File {f} not found")
        sys.exit()

def read_in(f, format):
    if format == "ms":
        return read_msolve(f)
    if format == "in":
        return read_hpXbred(f)
    if format == "magma":
        return read_magma(f)
    if format == "sobj":
        return read_sage(f)
    if format == "sat":
        return read_sat(f)

def write_msolve(f, system, variables):
    try:
        with open(f, "w") as fd:
            fd.write(f"{",".join(variables)}\n2\n")
            for poly in system[:-1]:
                fd.write(f"{"+".join(poly)},\n")
            fd.write(f"{"+".join(system[-1])}")
    except:
        print(f"Error opening or writing file {f}.")
        sys.exit()

def write_hpXbred(f, system, variables):
    try:
        with open(f, "w") as fd:
            fd.write(f"{",".join(variables)}\n")
            for poly in system[:-1]:
                line = "+".join(poly)
                if "^2" in line:
                    continue
                fd.write(f"{line}\n")
            line = "+".join(system[-1])
            if "^2" in line:
                return
            fd.write(f"{line}")
    except:
        print(f"Error opening or writing file {f}.")
        sys.exit()

def write_magma(f, system, variables):
    try:
        with open(f, "w") as fd:
            fd.write("F := GaloisField(2);\n")
            fd.write(f"Field<{",".join(variables)}> := BooleanPolynomialRing({len(variables)}, \"grevlex\");\n")
            poly_str = "["
            for i in range(len(system)):
                line = f"f{i} := {"+".join(system[i])};\n"
                fd.write(line)
                poly_str += f"f{i+1},"
            s = list(poly_str)
            s[-1] = "]"
            poly_str = "".join(s)            
            fd.write(f"PolynomialSystem := {poly_str};")
    except:
        print(f"Error opening or writing file {f}.")
        sys.exit()

def write_sage(f, system, variables):
    try:
        with open(f, "w") as fd:
            print()
    except:
        print(f"Error opening or writing file {f}.")
        sys.exit()

def write_sat(f, system, variables):
    try:
        with open(f, "w") as fd:
            print()
    except:
        print(f"Error opening or writing file {f}.")
        sys.exit()

def write_out(f, format, system, variables):
    if format == "ms":
        return write_msolve(f, system, variables)
    if format == "in":
        return write_hpXbred(f, system, variables)
    if format == "magma":
        return write_magma(f, system, variables)
    if format == "sobj":
        return write_sage(f, system, variables)
    if format == "sat":
        return read_sat(f, system, variables)

if __name__ == "__main__":
    in_f, out_f = parse_args()
    format_in, format_out = check_formats(in_f, out_f)
    system, variables = read_in(in_f, format_in)
    print(system)
    write_out(out_f, format_out, system, variables)