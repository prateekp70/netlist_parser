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
            port_name = port_match.group(3)
            current_module.ports.append((port_name, port_type))
            
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
            net_names = net_match.group(2).split(',')
            for net_name in net_names:
                net_name = net_name.strip()
                current_net = VerilogNet(net_name)
                current_module.nets.append(current_net)



    return modules

# Usage:
modules = parse_verilog('netlist.v.txt')

for m in modules:
    print("Module Name :", m.name)
    
    print("\nPorts:")
    for port in m.ports:
        print(f"  Name: {port[0]}, Type: {port[1]}")
    
    print("\nInstances:")
    for instance in m.instances:
        print(f"  Instance Name: {instance.name}, Cell Type: {instance.cell_type}")
        print("  Connections:")
        for port, net in instance.connections.items():
            print(f"    Port: {port}, Net: {net}")
    
    print("\nNets:")
    for net in m.nets:
        print(f"  Net Name: {net.name}")
        if net.pins:
            print("  Connected Pins:")
            for pin in net.pins:
                print(f"    Instance: {pin.instance.name}, Port: {pin.port}, Net: {pin.net}")

    print("\n" + "="*50 + "\n")  # Separator between modules

