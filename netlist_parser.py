import re

class VerilogModule:
    def __init__(self, name):
        self.name = name
        self.ports = []
        self.instances = []
        self.nets = []


class VerilogInstance:
    def __init__(self, name, cell_type):
        self.name = name
        self.cell_type = cell_type
        self.connections = {}


class VerilogNet:
    def __init__(self, name):
        self.name = name
        self.pins = []


class VerilogPin:
    def __init__(self, port, instance, net):
        self.port = port
        self.instance = instance
        self.net = net




# Path: netlist_parser.py


def parse_netlist(netlist_file):


    modules = []
    current_module = None


    with open(netlist_file, 'r') as f:
        lines = f.readlines()
   
    for line in lines:
        line = line.strip()


        if line.startswith('//') or not line:
            continue


        if line.startswith('module'):
            module_name = re.findall(r'module\s+(\w+)\s*\(', line)[0]
            current_module = VerilogModule(module_name)
            modules.append(current_module)


        if current_module and line.startswith('endmodule'):
            current_module = None
       
        if current_module is not None:
            if line.startswith('input') or line.startswith('output') or line.startswith('inout'):
                port_type = re.findall(r'(input|output|inout)', line)[0]
                port_name = re.findall(r'\s+(\w+)', line)[0]
                current_module.ports.append((port_name, port_type))


            if line.startswith('wire'):
                net_name = re.findall(r'wire\s+\[\d+:\d+\]\s+(\w+);', line)[0]
                current_module.nets.append(VerilogNet(net_name))
            if line.startswith('assign'):
                continue
            else:
                match = re.match(r'(\w+)\s+(\w+)\s*\(', line)
                if match:
                    cell_type, instance_name = match.groups()
                    instance = VerilogInstance(instance_name, cell_type)
                    current_module.instances.append(instance)
                    connections = re.findall(r'\.(\w+)\(([^)]+)\)', line)
                    for port, net in connections:
                        instance.connections[port] = net
    return modules




modules = parse_netlist('netlist.txt')
# # print(module[0].name)
# # print(module[0].instances[1].name)
# # print(module[0].instances[0].cell_type)
# # print(module[0].instances[0].connections)
# # print(module[0].nets[1].name)


# for i in module:
#     print('Module : ',i.name)
#     print('ports : ',i.ports)
#     print('instances : ',i.instances)
#     print('nets : ',i.nets)
#     print('\n')

def print_object_attributes(obj, indent=0):
    for attr in dir(obj):
        if not callable(getattr(obj, attr)) and not attr.startswith("__"):
            value = getattr(obj, attr)
            print(" " * indent + f"{attr}: {value}")
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, (VerilogModule, VerilogInstance, VerilogNet, VerilogPin)):
                        print_object_attributes(item, indent + 2)
            elif isinstance(value, (VerilogModule, VerilogInstance, VerilogNet, VerilogPin)):
                print_object_attributes(value, indent + 2)

for i in modules:
    print_object_attributes(i)
    # print(dir(i))
    print('\n')