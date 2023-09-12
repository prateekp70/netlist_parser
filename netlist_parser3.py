import re
from neo4j import GraphDatabase
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
            port_width = port_match.group(2).strip() if port_match.group(2) else ''
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
            if port_width:
                verilog_code += f"  {port_type} {port_width} {port_name},\n"
            else:
                verilog_code += f"  {port_type} {port_name},\n"
        verilog_code = verilog_code.rstrip(',\n') + "\n);\n\n"

        # Wire declarations
        wire_declarations = {}
        for net in module.nets:
            wire_declarations[net.name] = f"    wire {net.width} {net.name};\n"
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

def save_to_neo4j(modules):
    uri = "neo4j+s://1ec1c605.databases.neo4j.io"
    username = "neo4j"
    password = "pTjTGJjqSkVDxDc7J11olJ9hF2Ph_IHhwOF6avzbaiY"

    driver = GraphDatabase.driver(uri, auth=(username, password))

    with driver.session() as session:
        for module in modules:
            try:
                session.run("CREATE (m:Module {name: $name}) RETURN m", name=module.name)
            except Exception as e:
                print(f"Error creating module: {e}")

            for port in module.ports:
                try:
                    session.run("""
                        MATCH (m:Module {name: $module_name})
                        CREATE (p:Port {name: $port_name, type: $port_type, width: $port_width})-[:BELONGS_TO]->(m)
                    """, module_name=module.name, port_name=port[0], port_type=port[1], port_width=port[2])
                except Exception as e:
                    print(f"Error creating port: {e}")

            for instance in module.instances:
                try:
                    session.run("""
                        MATCH (m:Module {name: $module_name})
                        CREATE (i:Instance {name: $instance_name, cell_type: $cell_type})-[:PART_OF]->(m)
                    """, module_name=module.name, instance_name=instance.name, cell_type=instance.cell_type)
                except Exception as e:
                    print(f"Error creating instance: {e}")

                for port_name, net_name in instance.connections.items():
                    try:
                        session.run("""
                            MATCH (i:Instance {name: $instance_name})
                            CREATE (p:Pin {port: $port_name, net: $net_name})-[:CONNECTED_TO]->(i)
                        """, instance_name=instance.name, port_name=port_name, net_name=net_name)
                    except Exception as e:
                        print(f"Error creating pin: {e}")

            for net in module.nets:
                try:
                    session.run("""
                        MATCH (m:Module {name: $module_name})
                        CREATE (n:Net {name: $net_name, width: $net_width})-[:PART_OF]->(m)
                    """, module_name=module.name, net_name=net.name, net_width=net.width)
                except Exception as e:
                    print(f"Error creating net: {e}")

            for assign in module.assignments:
                try:
                    session.run("""
                        MATCH (m:Module {name: $module_name})
                        CREATE (a:Assignment {statement: $assign_statement})-[:PART_OF]->(m)
                    """, module_name=module.name, assign_statement=assign)
                except Exception as e:
                    print(f"Error creating assignment: {e}")

    driver.close()

# Usage:
modules = parse_verilog('netlist.v.txt')
verilog_code = generate_verilog(modules)
save_to_neo4j(modules)

# Storing the generated Verilog code in a .txt file
with open('generated_verilog.txt', 'w+') as f:
    f.write(verilog_code)

print("Verilog code has been written to generated_verilog.txt")

