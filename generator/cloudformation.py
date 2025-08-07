from jinja2 import Environment, FileSystemLoader
import os

def generate_cloudformation_template(components):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("cloudformation_template.j2")
    
    # Normalize resource names
    for c in components:
        c["resource_name"] = c["name"].replace(" ", "").replace("-", "").replace("_", "")

    return template.render(components=components)
