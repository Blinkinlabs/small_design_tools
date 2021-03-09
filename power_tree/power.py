import json

# types supported:
# "input": input from an external supply (wall wart, etc)
# "dcdc": DC-DC switching regulator, either boost or buck. These are assumed to have a fixed efficiency
# "linear": Linear regulator. The efficiency of these is determined by the difference between the input and output voltages.
# "load": Something that sinks power, modeled as a current sink

class powersupply:
    def __init__(self, name, voltage, loads):
        self.name = name
        self.voltage = voltage
        self.loads = loads

    def maxWattage(self, supply):
        state = {}

        state["efficiency"] = 1

        # Output load is equal to voltage * sum of current to all loads
        state["output_power"] = sum([load.maxWattage(self)["input_power"] for load in self.loads])

        state["output_voltage"] = self.voltage
        state["output_current"] = state["output_power"]/state["output_voltage"]

        state["input_voltage"] = state["output_voltage"]
        state["input_power"] = state["output_power"]
        state["input_current"] = state["output_current"] 

        return state

class dcdc:
    def __init__(self, name, voltage, efficiency, loads):
        self.name = name
        self.voltage = voltage
        self.efficiency = efficiency
        self.loads = loads

    def maxWattage(self, supply):
        """ Calculate the maximum expected load on this supply, in Watts """

        state = {}

        state["efficiency"] = self.efficiency

        # Output load is equal to voltage * sum of current to all loads
        state["output_power"] = sum([load.maxWattage(self)["input_power"] for load in self.loads])

        state["output_voltage"] = self.voltage
        state["output_current"] = state["output_power"]/state["output_voltage"]

        state["input_voltage"] = supply.voltage
        state["input_power"] = state["output_power"]/state["efficiency"]
        state["input_current"] = state["input_power"]/state["input_voltage"]

        return state

class linear:
    def __init__(self, name, voltage, loads):
        self.name = name
        self.voltage = voltage
        self.loads = loads

    def maxWattage(self, supply):
        """ Calculate the maximum expected load on this supply, in Watts """

        state = {}

        # # Efficiency is the ratio of output voltage to input voltage
        state["efficiency"] = self.voltage/supply.voltage

        # Output load is equal to voltage * sum of current to all loads
        state["output_power"] = sum([load.maxWattage(self)["input_power"] for load in self.loads])

        state["output_voltage"] = self.voltage
        state["output_current"] = state["output_power"]/state["output_voltage"]

        state["input_voltage"] = supply.voltage
        state["input_power"] = state["output_power"]/state["efficiency"]
        state["input_current"] = state["input_power"]/state["input_voltage"]

        return state

class load:
    def __init__(self, name, max_current):
        self.name = name
        self.max_current = max_current

    def maxWattage(self, supply):
        """ Calculate the maximum expected load, in Watts """
        # l = self.max_current*supply.voltage
        # return self.max_current*supply.voltage

        state = {}
        state["input_voltage"] = supply.voltage
        state["input_current"] = self.max_current
        state["input_power"] = state["input_voltage"] * state["input_current"]

        return state

def decode_tree(dct):
    if "type" not in dct:
        # TODO: Raise exception
        return dct

    t = dct.pop("type")
    if t == "powersupply":
        return powersupply(**dct)
    elif t == "dcdc":
        return dcdc(**dct)
    elif t == "linear":
        return linear(**dct)
    elif t == "load":
        return load(**dct)

with open('example.json', 'r') as json_file:
    powertree = json.load(json_file, object_hook=decode_tree)

def write_dot_node(node, supply, file):
    # if this is a voltage supply
    if hasattr(node,"loads"):
        state = node.maxWattage(supply)
        
        if supply==None:
            file.write('  "{}" [label="{}\\ninput: {:.2f}W ({:.2f}A@{:.2f}V)",style="filled"];\n'
                .format(node.name,node.name,
                    state["input_power"],state["input_current"],state["input_voltage"],
                    )
                )

        else:
            file.write('  "{}" [label="{}\\ninput: {:.2f}W ({:.2f}A@{:.2f}V)\\noutput: {:.2f}W ({:.2f}A@{:.2f}V)\\nEfficiency:{:.0f}% waste:{:.2f}W",style="filled"];\n'
                .format(node.name,node.name,
                    state["input_power"],state["input_current"],state["input_voltage"],
                    state["output_power"],state["output_current"],state["output_voltage"],
                    state["efficiency"]*100,state["input_power"]-state["output_power"]
                    )
                )

        for load in node.loads:
            file.write('  "{}":e -> "{}":w [];\n'.format(node.name,load.name))
            write_dot_node(load, node, file)
    else:
        state = node.maxWattage(supply)
        file.write('  "{}" [label="{}\\n{:.2f}W ({:.2f}A@{:.2f}V)"];\n'
            .format(node.name,node.name,state["input_power"],state["input_current"],state["input_voltage"]))


dotfile_header="""digraph test {
  rankdir=LR;
  splines=false;
  rank="same";

  node [fixedsize="true", width="3", height="1", shape="polygon",sides=4]
  graph [style="invis"]"""

with open('example.dot', 'w') as dotfile:
    dotfile.write(dotfile_header)

    write_dot_node(powertree, None, dotfile)

    dotfile.write("}")