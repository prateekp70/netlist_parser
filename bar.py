import re

class VerilogModule:
    def __init__(self, name):
        self.name = name
        self.ports = []
        self.instances = []
        self.nets = []

    def __repr__(self):
        return f'Module: {self.name}, Ports: {self.ports}, Nets: {self.nets}, Instances: {self.instances}'

class VerilogInstance:
    def __init__(self, name, cell_type):
        self.name = name
        self.cell_type = cell_type
        self.connections = {}

    def __repr__(self):
        return f'Instance: {self.name}, Cell Type: {self.cell_type}, Connections: {self.connections}'

class VerilogNet:
    def __init__(self, name):
        self.name = name
        self.pins = []

    def __repr__(self):
        return f'Net: {self.name}'

# Function to parse the netlist
def parse_netlist(netlist_file):

    modules = []
    current_module = None

    with open(netlist_file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Skip comments and empty lines
        if line.startswith('//') or not line:
            continue

        # Identify and store module details
        if line.startswith('module'):
            module_name = re.findall(r'module\s+(\w+)', line)[0]
            current_module = VerilogModule(module_name)
            modules.append(current_module)

        # Identify end of a module
        elif current_module and line.startswith('endmodule'):
            current_module = None

        # If inside a module, parse the different components
        elif current_module is not None:
            
            # Parse ports
            if re.match(r'(input|output|inout)', line):
                port_type, port_name = re.findall(r'(input|output|inout)\s+\[?\d*:\d*\]?\s+(\w+)', line)[0][0]
                current_module.ports.append((port_name, port_type))

            # Parse nets
            elif line.startswith('wire'):
                net_name = re.findall(r'wire\s+\[?\d*:\d*\]?\s+(\w+)', line)[0]
                current_module.nets.append(VerilogNet(net_name))

            # Parse instances
            elif re.search(r'\s*\w+\s+\w+\s*\(.*\)\s*;', line):
                cell_type, instance_name = re.findall(r'(\w+)\s+(\w+)\s*\(', line)[0]
                instance = VerilogInstance(instance_name, cell_type)
                current_module.instances.append(instance)
                connections = re.findall(r'\.(\w+)\s*\(\s*([^)]+)\s*\)', line)
                for port, net in connections:
                    instance.connections[port] = net

    return modules

# Parse the netlist and print the module objects
module = parse_netlist('netlist.txt')
for i in module:
    print(i)
