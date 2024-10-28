import PySimpleGUI as sg
import os
import subprocess

# Function to generate the RSU input rows dynamically, with the ability to pre-fill existing values
def generate_rsu_table(num_rsus, values):
    layout = []
    for i in range(num_rsus):
        layout.append([sg.Text(f'RSU {i+1}'),
                       sg.Input(default_text=values.get(f'rsu_{i}_x', '0'), size=(5,1), key=f'rsu_{i}_x'),
                       sg.Input(default_text=values.get(f'rsu_{i}_y', '0'), size=(5,1), key=f'rsu_{i}_y'),
                       sg.Input(default_text=values.get(f'rsu_{i}_z', '0'), size=(5,1), key=f'rsu_{i}_z')])
    return layout

def initialisation_window(num_rsus=1, saved_values=None):
    if saved_values is None:
        saved_values = {}

    rsu_table_layout = generate_rsu_table(num_rsus, saved_values)
    
    # Network and Simulation parameters
    network_layout = [
        sg.Text('Network and Simulation Parameters')
        [sg.Text('Network'), sg.Input(default_text=saved_values.get('network_name', ''), key='network_name')],
        [sg.Text('Playground Size')],
        [sg.Text('X'), sg.Spin([i for i in range(0, 5000)], initial_value=saved_values.get('pg_x', 2500), size=(5,1), key='pg_x'),
         sg.Text('Y'), sg.Spin([i for i in range(0, 5000)], initial_value=saved_values.get('pg_y', 2500), size=(5,1), key='pg_y'),
         sg.Text('Z'), sg.Spin([i for i in range(0, 5000)], initial_value=saved_values.get('pg_z', 50), size=(5,1), key='pg_z')],
        [sg.Text('Time Limit (s)'), sg.Spin([i for i in range(0, 100001)], initial_value=saved_values.get('time_limit', 1000), size=(6,1), key='time_limit')]
    ]

    # NIC Parameters
    nic_layout = [
        [sg.Text('NIC Parameters')]
        [sg.Checkbox('Send Direct?', default=saved_values.get('send_direct', False), key='send_direct')],
        [sg.Text('Max Interfacing Distance'), sg.Spin([i for i in range(0, 10001)], initial_value=saved_values.get('max_interface_distance', 500), size=(5,1), key='max_interface_distance')],
        [sg.Checkbox('Draw Max Interfacing Distance?', default=saved_values.get('drawMaxIntf', False), key='drawMaxIntf')],
        [sg.Checkbox('Use Service Channels?', default=saved_values.get('use_service_channels', False), key='use_service_channels')],
        [sg.Text('TX Power (mW)'), sg.Spin([i for i in range(0, 1001)], initial_value=saved_values.get('tx_power', 20), size=(5,1), key='tx_power')],
        [sg.Text('Bitrate (Mbps)'), sg.Spin([i for i in range(0, 101)], initial_value=saved_values.get('bitrate', 6), size=(5,1), key='bitrate')],
        [sg.Text('Min Power Level (dBm)'), sg.Spin([i for i in range(0, 1001)], initial_value=saved_values.get('min_power_level', 0), size=(5,1), key='min_power_level')],
        [sg.Checkbox('Use Noise Floor?', default=saved_values.get('use_noise_floor', False), key='use_noise_floor')],
        [sg.Text('Noise (dBm)'), sg.Spin([i for i in range(-100, 101)], initial_value=saved_values.get('noise_floor', -95), size=(6,1), key='noise_floor')],
        [sg.Text("Noise Decider File Name"), sg.Input(default_text=saved_values.get('noisedecider'), key='noisedecider')],
        [sg.Text("Analogue Models File Name"), sg.Input(default_text=saved_values.get('analogue'), key='analogue')],
        [sg.Checkbox('Use Propagation Delay?', default=saved_values.get('use_prop_delay', False), key='use_prop_delay')],
        [sg.Text("Antenna File"), sg.Input(default_text=saved_values.get('antenna'), key='antenna')],
        [sg.Text('Antenna Offset Y'), sg.Spin([i for i in range(-1000, 1001)], initial_value=saved_values.get('antenna_offset_y', 0), size=(6,1), key='antenna_offset_y')],
        [sg.Text('Antenna Offset Z'), sg.Spin([i for i in range(-1000, 1001)], initial_value=saved_values.get('antenna_offset_z', 0), size=(6,1), key='antenna_offset_z')]
    ]

    # Mobility Settings
    mobility_layout = [
        [sg.Text("Mobility Settings", size=(5,5))],
        [sg.Text("Enter the initial node coordinates")],
        [sg.Text('X:'), sg.Spin([i for i in range(0, 5000)], initial_value=saved_values.get('xmob'), key='xmob'), sg.Text('Y'), sg.Spin([i for i in range(0, 5000)],initial_value=saved_values.get('ymob'), key='ymob'),sg.Text('Z:'), sg.Spin([i for i in range(0, 5000)],initial_value=saved_values.get('zmob'), key='zmob')],
        [sg.Checkbox('Set Host Speed?', default=saved_values.get('set_hostspeed', False), key='set_hostspeed')],
        [sg.Text('Number of Accidents'), sg.Spin([i for i in range(0, 101)], initial_value=saved_values.get('num_accidents', 1), size=(5,1), key='num_accidents')],
        [sg.Text('Simulation Time of Accident(s)'), sg.Spin([i for i in range(0, 10000)], initial_value=saved_values.get('accident_start', 100), size=(6,1), key='accident_start')],
        [sg.Text('Duration (s)'), sg.Spin([i for i in range(0, 1001)], initial_value=saved_values.get('accident_duration', 30), size=(6,1), key='accident_duration')]
    ]

    #TraCIScenarioManager Parameters
    traci_layout = [
        [sg.Text(text="TraCIScenarioManager Parameters")],
        [sg.Text("Update Interval"), sg.Spin([i for i in range(0, 1000)], initial_value=saved_values.get('updateInt'), key='updateInt')],
        [sg.Text("Host"), sg.Input(default_text=saved_values.get('host'), key="host")],
        [sg.Checkbox(text="Auto Shutdown?", default=saved_values.get('autoshutdown', False), key="autoshutdown")],
        [sg.Text("Launch Config File Name"), sg.Input(default_text=saved_values.get('launchconfig'), key='launchconfig')]
    ]

    #RSU Settings Parameters
    rsu_layout = [
        [sg.Text('RSU Parameters')]
        [sg.Text('Num of RSUs'), sg.Spin([i for i in range(1, 101)], initial_value=num_rsus, key='num_rsus', size=(3,1), enable_events=True)],
        [sg.Text('RSU Positions (X, Y, Z)')],
        *rsu_table_layout,
        [sg.Text("Application Type File Name"), sg.Input(default_text=saved_values.get('appltype'), key='appltype')],
        [sg.Text('Application Header Length (bit)'), sg.Spin([i for i in range(0, 10000)], initial_value=saved_values.get('applhead', 100), size=(6,1), key='applhead')],
        [sg.Checkbox('Send Beacons?', default=saved_values.get('sendbeacon', False), key='sendbeacon')],
        [sg.Text('Interval (s)'), sg.Spin([i for i in range(1, 1000)], initial_value=saved_values.get('beacon_interval', 1), size=(6,1), key='beacon_interval')],
        [sg.Text('Beacon Priority'), sg.Spin([i for i in range(0, 9)], initial_value=saved_values.get('beacon_user_priority', 0), size=(3,1), key='beacon_user_priority'),
         sg.Text('Data Priority'), sg.Spin([i for i in range(0, 9)], initial_value=saved_values.get('data_user_priority', 0), size=(3,1), key='data_user_priority')]
    ]

    # Tabbed layout to keep things compact
    layout = [
        [sg.TabGroup([[sg.Tab('Network and Simulation', network_layout), 
                       sg.Tab('RSU', rsu_layout), 
                       sg.Tab('NIC', nic_layout),
                       sg.Tab('Mobility', mobility_layout),
                       sg.Tab('traci_layout', traci_layout)]])],
        [sg.Button('Submit'), sg.Button('Cancel')]
    ]
    
    return sg.Window('OMNeT++ Initialisation Configuration', layout)

def main_window():
    layout = [
        [sg.Text('Welcome to the V2X Simulation Tool!')],
        [sg.Text('This program will create an OMNeT++ initialisation file with your given parameters! ')],
        [sg.Text('Click "Next" to get started!')],
        [sg.Button('Next'), sg.Button('Cancel')]
    ]
    return sg.Window('V2X Simulation Setup', layout)

def write_to_ini(values):
    """Create omnetpp.ini file based on the values provided."""
    with open("omnetpp.ini", "w") as f:
        f.write("[General]\n")
        f.write(f"cmdenv-express-mode = true\n")
        f.write(f"cmdenv-autoflush = true\n")
        f.write(f"cmdenv-status-frequency = 1s\n")
        f.write(f"**.cmdenv-log-level = info\n")
        f.write(f"image-path = ../../images\n")
        f.write(f"network = {values['network_name']}\n")
        f.write(f"debug-on-errors = true\n")
        f.write(f"print-undisposed = true\n")
        f.write(f"sim-time-limit = {values['time_limit']}s\n")
        f.write(f"**.scalar-recording = true\n")
        f.write(f"**.vector-recording = true\n")
        f.write(f"*.playgroundSizeX = {values['pg_x']}m\n")
        f.write(f"*.playgroundSizeY = {values['pg_y']}m\n")
        f.write(f"*.playgroundSizeZ = {values['pg_z']}m\n")
        f.write(f"*.annotations.draw = true\n")
        f.write(f'*.obstacles.obstacles = xmldoc("{values["launchconfig"]}, "//AnalogueModel[@type=\'SimpleObstacleShadowing\']/obstacles"")"")\n')
        f.write(f"*.manager.updateInterval = {values['updateInt']}s\n")
        f.write(f'*.manager.host = "{values['launchconfig']}"\n')
        f.write(f"*.manager.port = {values['9999']}\n")
        f.write(f"*.manager.autoShutdown = {values['autoshutdown']}\n")
        f.write(f'*.manager.launchConfig = xmldoc("{values['launchconfig']}"\n')
        f.write(f"*.numRSUs = {values['num_rsus']}\n")
        for i in range(values['num_rsus']):
            f.write(f"*.rsu[{i}].mobility.X = {values[f'rsu_{i}_x']}m\n")
            f.write(f"*.rsu[{i}].mobility.Y = {values[f'rsu_{i}_y']}m\n")
            f.write(f"*.rsu[{i}].mobility.Z = {values[f'rsu_{i}_z']}m\n")
        f.write(f"*.rsu[*].applType = ""TraCIDemoRSU11p""")
        f.write(f"*.rsu[*].appl.headerLength = {values['applhead']} bit")
        f.write(f"*.sendBeacons = {values['send_beacons']}\n")
        f.write(f"*.rsu[*].appl.dataOnSch = true \n")
        f.write(f"*.beaconInterval = {values['beacon_interval_time']}s\n")
        f.write(f"*.beaconUserPriority = {values['beacon_user_priority']}\n")
        f.write(f"*.dataUserPriority = {values['data_user_priority']}\n")
        f.write(f"*.rsu[*].nic.phy80211p.antennaOffsetZ = 0 m\n")
        f.write(f"*.connectionManager.maxInterfDist = {values['max_interface_distance']}m\n")
        f.write(f"*.connectionManager.drawMaxIntfDist = {values['drawMaxIntf']}\n")
        f.write(f"*.**.nic.mac1609_4.useServiceChannel = {values['use_service_channel']}\n")
        f.write(f"*.**.nic.mac1609_4.txPower = {values['tx_power']}mW\n")
        f.write(f"*.**.nic.mac1609_4.bitrate = {values['bitrate']}Mbps\n")
        f.write(f"*.**.nic.phy80211p.minPowerLevel = {values['min_power_level']}dBm\n")
        f.write(f"*.**.nic.phy80211p.useNoiseFloor = {values['use_noise_floor']}\n")
        f.write(f"*.**.nic.phy80211p.noiseFloor = {values['noise_floor']}dBm\n")
        f.write(f'*.**.nic.phy80211p.decider = xmldoc("{values['launchconfig']}")\n')
        f.write(f'*.**.nic.phy80211p.analogueModels = xmldoc("{values['launchconfig']}")\n')
        f.write(f"*.**.nic.phy80211p.usePropagationDelay = {values['use_prop_delay']}\n")
        f.write(f'*.**.nic.phy80211p.antenna = xmldoc("{values['antenna']}", ""/root/Antenna[@id=\'monopole\']"")\n')
        f.write(f"*.node[*].nic.phy80211p.antennaOffsetY = {values['antenna_offset_y']} m\n")
        f.write(f"*.connectionManager.sendDirect = {values['send_direct']}\n")
        f.write(f"*.node[*].nic.phy80211p.antennaOffsetZ = {values['antenna_offset_z']} m")



def write_to_ned(values):
    """Create a simple NED file based on the values provided."""
    with open(f"{values['network_name']}.ned", "w") as f:
        f.write(f"import org.car2x.veins.nodes.RSU;")
        f.write(f"import org.car2x.veins.nodes.Scenario;\n")
        f.write(f"network {values['network_name']} extends Scenario"'{'"\n")
        f.write("    submodules:\n")
        for i in range(values['num_rsus']):
            f.write(f"        rsu[{i}]: RSU ""{\n")
            f.write(f"            @display(""p=150,140;i=veins/sign/yellowdiamond;is=vs"');')
            f.write(f"        "'}'"\n")
        f.write("}\n")

window = main_window()
num_rsus = 1
saved_values = {}

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break

    if event == 'Next':
        window.close()
        window = initialisation_window(num_rsus, saved_values)

    if event == 'num_rsus':
        num_rsus = int(values['num_rsus'])
        saved_values.update(values)
        window.close()
        window = initialisation_window(num_rsus, saved_values)

    if event == 'Submit':
        write_to_ini(values)
        write_to_ned(values)
        sg.popup("Configuration Saved!", saved_values)
        print("Configuration saved: ", saved_values)
        break

window.close()
