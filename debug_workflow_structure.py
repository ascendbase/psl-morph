import json

# Load and analyze the workflow structure
with open('comfyui_workflows/face_swap_with_intensity.json', 'r') as f:
    workflow = json.load(f)

print("🔍 Workflow Structure Analysis")
print("=" * 50)

print(f"Top-level keys: {list(workflow.keys())}")
print(f"Workflow type: {type(workflow)}")

if 'nodes' in workflow:
    nodes = workflow['nodes']
    print(f"\nFound 'nodes' array with {len(nodes)} nodes")
    
    load_image_nodes = []
    for i, node in enumerate(nodes):
        if isinstance(node, dict):
            node_type = node.get('type', 'Unknown')
            print(f"Node {i}: {node_type}")
            if node_type == 'LoadImage':
                load_image_nodes.append(i)
                print(f"  ✅ LoadImage node found at index {i}")
                print(f"  Title: {node.get('title', 'No title')}")
    
    print(f"\nTotal LoadImage nodes found: {len(load_image_nodes)}")
else:
    print("\nNo 'nodes' array found. Checking direct properties...")
    for key, value in workflow.items():
        if isinstance(value, dict):
            node_type = value.get('type', 'Unknown')
            print(f"Key {key}: {node_type}")
