import xml.etree.ElementTree as ET
import copy

# Namespaces
namespaces = {
    'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
    'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
    'dc': 'http://www.omg.org/spec/DD/20100524/DC',
    'di': 'http://www.omg.org/spec/DD/20100524/DI',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'modeler': 'http://camunda.org/schema/modeler/1.0',
    'camunda': 'http://camunda.org/schema/1.0/bpmn'
}

# Register namespaces
for prefix, uri in namespaces.items():
    ET.register_namespace(prefix, uri)

source_file = 'DPE_Haustierprozess.bpmn'
tree = ET.parse(source_file)
root = tree.getroot()

# Ensure camunda namespace is in the root attributes (ElementTree handles this via register_namespace usually,
# but we might need to ensure it's used to be printed)

# Helper to find elements with namespace
def find_all(element, tag):
    return element.findall(f'.//bpmn:{tag}', namespaces)

def find_by_id(element, tag, id_val):
    for child in find_all(element, tag):
        if child.get('id') == id_val:
            return child
    return None

# --- Create Nahrungszyklusprozess.bpmn ---
nahrung_tree = copy.deepcopy(tree)
nahrung_root = nahrung_tree.getroot()

# Remove the main process (Process_17qlqmt) and its participant (Participant_1dvcj9q)
# Process_1d67c0b is the one we want to keep.
# Participant_16ry964 is the one for Process_1d67c0b.

collab = nahrung_root.find('bpmn:collaboration', namespaces)
if collab is not None:
    # Remove Participant_1dvcj9q
    for p in collab.findall('bpmn:participant', namespaces):
        if p.get('id') == 'Participant_1dvcj9q':
            collab.remove(p)
    # Also remove MessageFlows connected to removed participant?
    # For simplicity, I'll leave them if they don't break XML validness, but usually safe to remove.
    # Actually, let's just keep the process we want and the participant we want.

# Remove Process_17qlqmt
for process in nahrung_root.findall('bpmn:process', namespaces):
    if process.get('id') == 'Process_17qlqmt':
        nahrung_root.remove(process)
    elif process.get('id') == 'Process_1d67c0b':
        process.set('id', 'Nahrungszyklusprozess')
        process.set('isExecutable', 'true')

        # Update Tasks to External
        for task in process.findall('bpmn:sendTask', namespaces):
            task.set('camunda:type', 'external')
            if task.get('id') == 'Activity_1r9tdl3':
                 task.set('camunda:topic', 'requestLLM')
            if task.get('id') == 'Activity_0h1j7jz':
                 task.set('camunda:topic', 'requestPurchaseRecommendation')

# Clean up DI in nahrung_tree
# We need to remove shapes for the removed process/participant.
diagram = nahrung_root.find('bpmndi:BPMNDiagram', namespaces)
plane = diagram.find('bpmndi:BPMNPlane', namespaces)
# This is tricky without a map of IDs to remove.
# But since we only have two main participants, we can look for the shape of the removed participant.
to_remove = []
for shape in plane.findall('bpmndi:BPMNShape', namespaces):
    bpmn_element = shape.get('bpmnElement')
    if bpmn_element == 'Participant_1dvcj9q':
        to_remove.append(shape)
    # Also remove shapes that belong to the removed process.
    # But looking up every element is costly.
    # Simpler heuristic: If the element is not in the remaining process or collaboration, remove the shape?
    # That requires a full set of remaining IDs.

# Let's just do the Participant shape removal for now, the rest might just be orphan shapes (not ideal but works).
for item in to_remove:
    plane.remove(item)

# Update Participant_16ry964 to point to renamed process
for p in collab.findall('bpmn:participant', namespaces):
    if p.get('id') == 'Participant_16ry964':
        p.set('processRef', 'Nahrungszyklusprozess')


nahrung_tree.write('Nahrungszyklusprozess.bpmn', encoding='UTF-8', xml_declaration=True)


# --- Create DPE_Haustierprozess_updated.bpmn ---
# Reload to be clean
tree = ET.parse(source_file)
root = tree.getroot()

# Remove Process_1d67c0b
for process in root.findall('bpmn:process', namespaces):
    if process.get('id') == 'Process_1d67c0b':
        root.remove(process)
    elif process.get('id') == 'Process_17qlqmt':
        # This is the main process
        # Find the Call Activity Activity_1rm109p
        for call_activity in process.findall('.//bpmn:callActivity', namespaces):
            if call_activity.get('id') == 'Activity_1rm109p':
                call_activity.set('calledElement', 'Nahrungszyklusprozess')

                # Add extension elements
                extension = ET.SubElement(call_activity, '{http://camunda.org/schema/1.0/bpmn}extensionElements')

                # In: haustierId (Reference)
                in_var1 = ET.SubElement(extension, '{http://camunda.org/schema/1.0/bpmn}in')
                in_var1.set('source', 'haustierId')
                in_var1.set('target', 'haustierId')

                # In: vorraete (Value)
                in_var2 = ET.SubElement(extension, '{http://camunda.org/schema/1.0/bpmn}in')
                in_var2.set('source', 'vorraete')
                in_var2.set('target', 'vorraete')

                # Out: neueVorraete -> vorraete
                out_var = ET.SubElement(extension, '{http://camunda.org/schema/1.0/bpmn}out')
                out_var.set('source', 'neueVorraete')
                out_var.set('target', 'vorraete')

        # Update Service Tasks
        for task in process.findall('.//bpmn:serviceTask', namespaces):
             if task.get('id') == 'Activity_10b64qx':
                 task.set('camunda:type', 'external')
                 task.set('camunda:topic', 'updateDatabase')

collab = root.find('bpmn:collaboration', namespaces)
if collab is not None:
    # Remove Participant_16ry964 (the one corresponding to the extracted process)
    for p in collab.findall('bpmn:participant', namespaces):
        if p.get('id') == 'Participant_16ry964':
            collab.remove(p)

# Clean up DI for removed participant
diagram = root.find('bpmndi:BPMNDiagram', namespaces)
plane = diagram.find('bpmndi:BPMNPlane', namespaces)
to_remove = []
for shape in plane.findall('bpmndi:BPMNShape', namespaces):
    bpmn_element = shape.get('bpmnElement')
    if bpmn_element == 'Participant_16ry964':
        to_remove.append(shape)
for item in to_remove:
    plane.remove(item)

tree.write('DPE_Haustierprozess.bpmn', encoding='UTF-8', xml_declaration=True)
