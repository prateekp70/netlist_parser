import re

class VerilogModule:
    def __init__(self, name):
        self.name = name
        self.ports = []
        self.instances = []
        self.nets = []
        # Created a new instance variable to store assignments like assign SUM = sum;
        self.assignments = []

class VerilogInstance:
    def __init__(self, name, cell_type):
        self.name = name
        self.cell_type = cell_type
        self.connections = {}

class VerilogNet:
    def __init__(self, name):
        self.name = name
        self.width = ''
        self.pins = []

class VerilogPin:
    def __init__(self, port, instance, net):
        self.port = port
        self.instance = instance
        self.net = net

def parse_verilog(file_path):
    modules = []
    current_module = None
    current_instance = None
    inside_instance = False

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        
        if line.startswith('//') or not line:
            continue

        # Match module definition
        module_match = re.match(r'module (\w+)', line)
        if module_match:
            current_module = VerilogModule(module_match.group(1))
            modules.append(current_module)
        
        # Match port definition
        port_match = re.match(r'\s*(input|output|inout)(\s+\[\d+:\d+\])?\s+(\w+)', line)
        if port_match and current_module:          
            port_type = port_match.group(1)
            port_width = port_match.group(2) if port_match.group(2) else ''
            port_name = port_match.group(3)
            current_module.ports.append((port_name, port_type, port_width))
            
        # Match instance definition
        instance_match = re.match(r'\s*(?!module\b)(\w+)\s+(\w+)\s*\(', line)
        if instance_match and current_module:
            instance_type = instance_match.group(1)
            instance_name = instance_match.group(2)
            current_instance = VerilogInstance(instance_name, instance_type)
            current_module.instances.append(current_instance)
            inside_instance = True

        # Match connection definition
        if inside_instance and current_instance:
            for connection_match in re.finditer(r'\s*\.(\w+)\s*\(\s*([\w\[\]\'b]+)\s*\)', line):
                port_name = connection_match.group(1)
                net_name = connection_match.group(2)
                current_instance.connections[port_name] = net_name

                # Create a VerilogPin object
                pin = VerilogPin(port_name, current_instance, net_name)
                
                # Find the net object and add the pin to it
                for net in current_module.nets:
                    if net.name == net_name:
                        net.pins.append(pin)
                        break

        # Check for the end of the instance definition
        if line.strip().endswith(');'):
            inside_instance = False

        # Match Net definition
        net_match = re.match(r'\s*wire\s+(\[.*\])?\s*([\w,]+)\s*;', line)
        if net_match and current_module:
            net_width = net_match.group(1) if net_match.group(1) else ''
            net_names = net_match.group(2).split(',')
            for net_name in net_names:
                net_name = net_name.strip()
                current_net = VerilogNet(net_name)
                current_net.width = net_width
                current_module.nets.append(current_net)

        # Match assign statements
        assign_match = re.match(r'\s*assign\s+(.*);', line)
        if assign_match and current_module:
            current_module.assignments.append(assign_match.group(1))            

    return modules

def generate_verilog(modules):
    verilog_code = ""
    for module in modules:
        # Module declaration
        verilog_code += f"module {module.name} (\n"
        for port in module.ports:
            port_type = port[1]
            port_width = port[2]
            port_name = port[0]
            verilog_code += f"    {port_type} {port_width} {port_name},\n"
        verilog_code = verilog_code.rstrip(',\n') + "\n);\n\n"

        # Wire declarations
        wire_declarations = {}
        for net in module.nets:
            wire_declarations[net.name] = f"    wire {net.width} {net.name};\n"

        # Adding wire declarations at the beginning of the module
        for net_declaration in wire_declarations.values():
            verilog_code += net_declaration

        # Instance declarations
        for instance in module.instances:
            verilog_code += f"    {instance.cell_type} {instance.name} ("
            for port, net in instance.connections.items():
                verilog_code += f".{port}({net}), "
            verilog_code = verilog_code.rstrip(', ') + ");\n"

        # Assignment statements
        for assign in module.assignments:
            verilog_code += f"    assign {assign};\n"

        verilog_code += "\nendmodule\n\n"

    return verilog_code

import re

class VerilogModule:
    def __init__(self, name):
        self.name = name
        self.ports = []
        self.instances = []
        self.nets = []
        # Created a new instance variable to store assignments like assign SUM = sum;
        self.assignments = []

class VerilogInstance:
    def __init__(self, name, cell_type):
        self.name = name
        self.cell_type = cell_type
        self.connections = {}

class VerilogNet:
    def __init__(self, name):
        self.name = name
        self.width = ''
        self.pins = []

class VerilogPin:
    def __init__(self, port, instance, net):
        self.port = port
        self.instance = instance
        self.net = net

def parse_verilog(file_path):
    modules = []
    current_module = None
    current_instance = None
    inside_instance = False

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        
        if line.startswith('//') or not line:
            continue

        # Match module definition
        module_match = re.match(r'module (\w+)', line)
        if module_match:
            current_module = VerilogModule(module_match.group(1))
            modules.append(current_module)
        
        # Match port definition
        port_match = re.match(r'\s*(input|output|inout)(\s+\[\d+:\d+\])?\s+(\w+)', line)
        if port_match and current_module:          
            port_type = port_match.group(1)
            port_width = port_match.group(2) if port_match.group(2) else ''
            port_name = port_match.group(3)
            current_module.ports.append((port_name, port_type, port_width))
            
        # Match instance definition
        instance_match = re.match(r'\s*(?!module\b)(\w+)\s+(\w+)\s*\(', line)
        if instance_match and current_module:
            instance_type = instance_match.group(1)
            instance_name = instance_match.group(2)
            current_instance = VerilogInstance(instance_name, instance_type)
            current_module.instances.append(current_instance)
            inside_instance = True

        # Match connection definition
        if inside_instance and current_instance:
            for connection_match in re.finditer(r'\s*\.(\w+)\s*\(\s*([\w\[\]\'b]+)\s*\)', line):
                port_name = connection_match.group(1)
                net_name = connection_match.group(2)
                current_instance.connections[port_name] = net_name

                # Create a VerilogPin object
                pin = VerilogPin(port_name, current_instance, net_name)
                
                # Find the net object and add the pin to it
                for net in current_module.nets:
                    if net.name == net_name:
                        net.pins.append(pin)
                        break

        # Check for the end of the instance definition
        if line.strip().endswith(');'):
            inside_instance = False

        # Match Net definition
        net_match = re.match(r'\s*wire\s+(\[.*\])?\s*([\w,]+)\s*;', line)
        if net_match and current_module:
            net_width = net_match.group(1) if net_match.group(1) else ''
            net_names = net_match.group(2).split(',')
            for net_name in net_names:
                net_name = net_name.strip()
                current_net = VerilogNet(net_name)
                current_net.width = net_width
                current_module.nets.append(current_net)

        # Match assign statements
        assign_match = re.match(r'\s*assign\s+(.*);', line)
        if assign_match and current_module:
            current_module.assignments.append(assign_match.group(1))            

    return modules

def generate_verilog(modules):
    verilog_code = ""
    for module in modules:
        # Module declaration
        verilog_code += f"module {module.name} (\n"
        for port in module.ports:
            port_type = port[1]
            port_width = port[2]
            port_name = port[0]
            verilog_code += f"    {port_type} {port_width} {port_name},\n"
        verilog_code = verilog_code.rstrip(',\n') + "\n);\n\n"

        # Wire declarations
        wire_declarations = {}
        for net in module.nets:
            wire_declarations[net.name] = f"    wire {net.width} {net.name};\n"

        # Adding wire declarations at the beginning of the module
        for net_declaration in wire_declarations.values():
            verilog_code += net_declaration

        # Instance declarations
        for instance in module.instances:
            verilog_code += f"    {instance.cell_type} {instance.name} ("
            for port, net in instance.connections.items():
                verilog_code += f".{port}({net}), "
            verilog_code = verilog_code.rstrip(', ') + ");\n"

        # Assignment statements
        for assign in module.assignments:
            verilog_code += f"    assign {assign};\n"

        verilog_code += "\nendmodule\n\n"

    return verilog_code

# Usage:
modules = parse_verilog('netlist.v.txt')
verilog_code = generate_verilog(modules)

# Storing the generated Verilog code in a .txt file
with open('generated_verilog.txt', 'w') as f:
    f.write(verilog_code)

print("Verilog code has been written to generated_verilog.txt")

