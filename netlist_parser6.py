import time
start = time.time()
import re
from neo4j import GraphDatabase

class VerilogModule:
    def __init__(self, name):
        self.name = name
        self.ports = []
        self.instances = []
        self.nets = []
        self.assignments = []

class VerilogInstance:
    def __init__(self, name, cell_type, ref_name):
        self.name = name
        self.cell_type = cell_type #Hierarchical or LibRefName
        self.pins = []
        self.refname = ref_name

class VerilogNet:
    def __init__(self, name, net_type):
        self.name = name
        self.pins = []
        self.connections = [] #Store the pin names that are part of the instance declarations in the module
        self.net_type = net_type

class VerilogPin:
    def __init__(self, pin, instance, net, direction):
        self.pin = pin
        self.instance = instance
        self.net = net
        self.direction = direction

class VerilogPort:
    def __init__(self,) -> None:
        self.name
        self.derived_net
        self.direction
        
    def isBus(self):
        pass
    def isClock(self):
        pass
    '''
    We can have more functions here
    '''



# Parsing the netlist file
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

        # Match module
        module_match = re.match(r'module (\w+)', line)
        if module_match:
            current_module = VerilogModule(module_match.group(1))
            modules.append(current_module)
        
        # Match port
        port_match = re.match(r'\s*(input|output|inout)(\s+\[\d+:\d+\])?\s+(\w+)', line)
        if port_match and current_module:          
            port_type = port_match.group(1)
            port_width = port_match.group(2).strip() if port_match.group(2) else ''
            port_name = port_match.group(3)
            current_module.ports.append((port_name, port_type, port_width))
            
        # Match Net
        net_match = re.match(r'\s*wire\s+(\[.*\])?\s*([\w,]+)\s*;', line)
        if net_match and current_module:
            net_width = net_match.group(1) if net_match.group(1) else ''
            net_names = net_match.group(2).split(',')
            for net_name in net_names:
                net_name = net_name.strip()
                current_net = VerilogNet(net_name)
                current_net.width = net_width
                current_module.nets.append(current_net)      
        
        # Match instance
        instance_match = re.match(r'\s*(?!module\b)(\w+)\s+(\w+)\s*\(', line)
        if instance_match and current_module:
            instance_type = instance_match.group(1)
            instance_name = instance_match.group(2)
            current_instance = VerilogInstance(instance_name, instance_type)
            current_module.instances.append(current_instance)
            inside_instance = True

        # Match connection
        if inside_instance and current_instance:
            for connection_match in re.finditer(r'\s*\.(\w+)\s*\(\s*([\w\[\]\'b]+)\s*\)', line):
                port_name = connection_match.group(1)
                net_name = connection_match.group(2)
                
                # Find the net object
                current_net = next((net for net in current_module.nets if net.name == net_name), None)
                
                if current_net:
                    # Create a VerilogPin object and add it to the net's pins list
                    pin = VerilogPin(port_name, current_instance, current_net)
                    current_net.pins.append(pin)
                    
                    # Store the connection in the instance's connections dictionary
                    current_instance.connections[port_name] = current_net
                else:
                    # If the net is not found, it might be a port or a constant value, 
                    # so we just store the net name in the instance's connections dictionary
                    current_instance.connections[port_name] = net_name
        
        # Match assign statements
        assign_match = re.match(r'\s*assign\s+(.*);', line)
        if assign_match and current_module:
            current_module.assignments.append(assign_match.group(1))            

        if line.strip().endswith(');'):
            inside_instance = False

    return modules

# Generate the verilog from the parsed objects
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
                if isinstance(net, VerilogNet):
                    net_name = net.name
                else:
                    net_name = net
                verilog_code += f".{port}({net_name}), "
            verilog_code = verilog_code.rstrip(', ') + ");\n"
        
        # Assignment statements
        for assign in module.assignments:
            verilog_code += f"    assign {assign};\n"

        verilog_code += "\nendmodule\n\n"

    return verilog_code

# Save to Neo4j database
def save_to_neo4j(modules):
    uri = "neo4j+ssc://9fe7f313.databases.neo4j.io"
    username = "neo4j"
    password = "dfqWAWE0-OhNd-EL3s9oEZAjDE3GsefCYI6bSG0xkDU"

    driver = GraphDatabase.driver(uri, auth=(username, password))

    import traceback

    with driver.session() as session:
        for module in modules:
            try:
                session.execute_write(create_module, module)
            except Exception as e:
                print(f"Error processing module {module.name}: {e}")
                print("Here's the traceback:")
                print(traceback.format_exc())

    driver.close()

# Save to Neo4j database
def create_module(tx, module):
    try:
        tx.run("CREATE (m:Module {name: $name}) RETURN m", name=module.name)
    except Exception as e:
        print(f"Error creating module {module.name}: {e}")

    try:
        for port in module.ports:
            tx.run("""
                MATCH (m:Module {name: $module_name})
                CREATE (p:Port {name: $port_name, type: $port_type, width: $port_width})-[:BELONGS_TO]->(m)
            """, module_name=module.name, port_name=port[0], port_type=port[1], port_width=port[2])
    except Exception as e:
        print(f"Error creating ports for module {module.name}: {e}")

    try:
        for instance in module.instances:
            tx.run("""
                MATCH (m:Module {name: $module_name})
                CREATE (i:Instance {name: $instance_name, cell_type: $cell_type})-[:PART_OF]->(m)
            """, module_name=module.name, instance_name=instance.name, cell_type=instance.cell_type)

            for port_name, net in instance.connections.items():
                if isinstance(net, VerilogNet):
                    tx.run("""
                        MATCH (i:Instance {name: $instance_name}), (m:Module {name: $module_name})
                        MERGE (n:Net {name: $net_name, width: $net_width})-[:PART_OF]->(m)
                        CREATE (p:Pin {port: $port_name})-[:CONNECTED_TO]->(i),
                               (p)-[:CONNECTS]->(n)
                    """, instance_name=instance.name, module_name=module.name, port_name=port_name, net_name=net.name, net_width=net.width)
                else:
                    tx.run("""
                        MATCH (i:Instance {name: $instance_name})
                        CREATE (p:Pin {port: $port_name, net: $net_name})-[:CONNECTED_TO]->(i)
                    """, instance_name=instance.name, port_name=port_name, net_name=net)
    except Exception as e:
        print(f"Error creating instances for module {module.name}: {e}")

    try:
        for net in module.nets:
            tx.run("""
                MATCH (m:Module {name: $module_name})
                MERGE (n:Net {name: $net_name, width: $net_width})-[:PART_OF]->(m)
            """, module_name=module.name, net_name=net.name, net_width=net.width)
    except Exception as e:
        print(f"Error creating nets for module {module.name}: {e}")

    try:
        for assign in module.assignments:
            tx.run("""
                MATCH (m:Module {name: $module_name})
                CREATE (a:Assignment {statement: $assign_statement})-[:PART_OF]->(m)
            """, module_name=module.name, assign_statement=assign)
    except Exception as e:
        print(f"Error creating assignments for module {module.name}: {e}")

# Fetch module objects from the database
def fetch_all_modules():
    modules = []
    
    uri = "neo4j+ssc://9fe7f313.databases.neo4j.io"
    username = "neo4j"
    password = "dfqWAWE0-OhNd-EL3s9oEZAjDE3GsefCYI6bSG0xkDU"
    driver = GraphDatabase.driver(uri, auth=(username, password))

    with driver.session() as session:
        # Fetch modules
        result = session.run("MATCH (m:Module) RETURN m.name AS name")
        
        for record in result:
            module_name = record['name']
            module = VerilogModule(module_name)
            
            # Fetch ports for this module
            ports_result = session.run("MATCH (p:Port)-[:BELONGS_TO]-(m:Module {name: $name}) RETURN p.name AS name, p.type AS type, p.width AS width", name=module_name)
            for port_record in ports_result:
                port_name = port_record['name']
                port_type = port_record['type']
                port_width = port_record['width']
                module.ports.append((port_name, port_type, port_width))

            # Fetch nets for this module
            nets_result = session.run("MATCH (n:Net)-[:PART_OF]-(m:Module {name: $name}) RETURN n.name AS name, n.width AS width", name=module_name)
            for net_record in nets_result:
                net_name = net_record['name']
                net_width = net_record['width']
                net = VerilogNet(net_name)
                net.width = net_width
                module.nets.append(net)

            # Fetch instances for this module
            instances_result = session.run("MATCH (i:Instance)-[:PART_OF]-(m:Module {name: $name}) RETURN i.name AS name, i.cell_type AS cell_type", name=module_name)
            for instance_record in instances_result:
                instance_name = instance_record['name']
                cell_type = instance_record['cell_type']
                instance = VerilogInstance(instance_name, cell_type)

                # Fetch connections for this instance
                connections_result = session.run("""
                    MATCH (p:Pin)-[:CONNECTED_TO]-(i:Instance {name: $name})
                    OPTIONAL MATCH (n:Net)-[:CONNECTS]-(p)
                    RETURN p.port AS port, COALESCE(n.name, p.net) AS net_name
                """, name=instance_name)
                
                for connection_record in connections_result:
                    port_name = connection_record['port']
                    net_name = connection_record['net_name']
                    
                    # Check if the net name matches an existing net in the module nets
                    connected_net = next((net for net in module.nets if net.name == net_name), None)
                    if connected_net:
                        instance.connections[port_name] = connected_net
                    else:
                        instance.connections[port_name] = net_name

                module.instances.append(instance)

            modules.append(module)

    return modules

modules = parse_verilog('netlist.v.txt')
parsed_verilog_code = generate_verilog(modules)
# save_to_neo4j(modules)

fetched_modules = fetch_all_modules()
fetched_verilog_code = generate_verilog(fetched_modules)

# Storing the generated Verilog code from parsed modules in a .txt file
with open('generated_verilog.txt', 'w+') as f:
    f.write(parsed_verilog_code)
    print("Verilog code has been written to generated_verilog.txt")

# Storing the generated Verilog code from fetched modules in a .txt file
with open('generated_verilog_db.txt', 'w+') as f:
    f.write(fetched_verilog_code)
    print("Verilog code has been written to generated_verilog_db.txt")

end = time.time()
time_taken = end - start
print("Execution time : ", time_taken,"seconds")



































# def fetch_all_modules():
#     modules = []

#     uri = "neo4j+ssc://9fe7f313.databases.neo4j.io"
#     username = "neo4j"
#     password = "dfqWAWE0-OhNd-EL3s9oEZAjDE3GsefCYI6bSG0xkDU"
#     driver = GraphDatabase.driver(uri, auth=(username, password))

#     with driver.session() as session:
#         query = """
#         MATCH (m:Module)
#         MATCH (m)<-[:BELONGS_TO]-(p:Port)
#         MATCH (m)<-[:PART_OF]-(n:Net)
#         MATCH (m)<-[:PART_OF]-(i:Instance)
#         MATCH (i)<-[:CONNECTED_TO]-(pin:Pin)-[:CONNECTS]->(connectedNet:Net)
#         RETURN m.name AS moduleName, 
#                COLLECT(DISTINCT {portName: p.name, portType: p.type, portWidth: p.width}) AS ports,
#                COLLECT(DISTINCT {netName: n.name, netWidth: n.width}) AS nets,
#                COLLECT(DISTINCT {instanceName: i.name, cellType: i.cell_type, connections: COLLECT({portName: pin.port, connectedNetName: connectedNet.name})}) AS instances
#         """

#         result = session.run(query)
#         for record in result:
#             module = VerilogModule(record['moduleName'])

#             for port_data in record['ports']:
#                 module.ports.append((port_data['portName'], port_data['portType'], port_data['portWidth']))

#             for net_data in record['nets']:
#                 net = VerilogNet(net_data['netName'])
#                 net.width = net_data['netWidth']
#                 module.nets.append(net)

#             for instance_data in record['instances']:
#                 instance = VerilogInstance(instance_data['instanceName'], instance_data['cellType'])

#                 for connection_data in instance_data['connections']:
#                     port_name = connection_data['portName']
#                     net_name = connection_data['connectedNetName']
#                     connected_net = next((net for net in module.nets if net.name == net_name), None)
#                     if connected_net:
#                         instance.connections[port_name] = connected_net
#                     else:
#                         instance.connections[port_name] = net_name

#                 module.instances.append(instance)

#             modules.append(module)

#     return modules