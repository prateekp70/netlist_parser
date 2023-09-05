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

modules = []
current_module = None

with open('netlist.txt','r+') as file:    
    data = file.readlines()

    for line in data:
        line = line.strip()
        
        if line.startswith('//') or not line:
            continue

        if line.startswith('module'):
            module_name = re.findall(r'module\s+(\w+)', line)[0]
            current_module = VerilogModule(module_name)
            modules.append(current_module)
        
        if module_name and line.startswith('endmodule'):
            module_name = None
        
        if current_module:
            if '(' in line:
                instance_name, cell_type = re.findall(r'(\w+)\s+(\w+)\s*\(', line)[0]
                print(instance_name)

        # if current_module:
        #     if '(' in line:
        #         instance_name, cell_type = re.findall(r'(\w+)\s+(\w+)\s*\(', line)[0]
        #         instance = VerilogInstance(instance_name, cell_type)
        #         current_module.instances.append(instance)
            
        #     if line.startswith('.') and current_module.instances:
        #         port_name, net_name = re.findall(r'\.(\w+)\s*\(\s*(\w+)\s*\)', line)[0]
        #         instance.connections[port_name] = net_name

                
            

            
            
            



    
