from inline_markdown import split_nodes_delimiter
from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
from markdown_blocks import markdown_to_html_node

import re
import markdown_blocks
import shutil
import os


def clear_public():
    if os.path.exists("public"):
        shutil.rmtree("public")
    os.mkdir("public")


def static_to_public(curr_path = ""):
    list = os.listdir(os.path.join("static", curr_path))
    for file in list:
        new_curr = os.path.join(curr_path, file)
        static_path = os.path.join("static", new_curr)
        public_path = os.path.join("public", new_curr)
        if os.path.isfile(static_path):
            print(f"FILE {static_path}")
            shutil.copy(static_path, os.path.dirname(public_path))
        else:
            os.mkdir(public_path)
            static_to_public(new_curr)

def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        if len(line) > 0 and line[0] == "#":
            return line.strip(" #")
    raise Exception("No title")

def generate_page(from_path, template_path, dest_path):
    try:
        f = open(from_path)
        t = open(template_path)
    except:
        print("Files not oppened")
        
    markdown = f.read()
    final_html = t.read()
    html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)
    final_html = final_html.replace("{{ Title }}", title)
    final_html = final_html.replace("{{ Content }}", html)
    
    
    dest_dir = os.path.dirname(dest_path)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    print("DEST DIR")
    print(dest_dir)
    
    with open(dest_path, "w") as file:
        file.write(final_html)
    

def generate_pages_recursive(curr_path = "", template_path = "template.html"):
    content_path = os.path.join("content", curr_path)
    
    list = os.listdir(content_path)
    for file in list:
        new_content_path = os.path.join(content_path, file)
        dest_path = os.path.join("public", curr_path, f"{os.path.splitext(file)[0]}.html")
        
        if os.path.isfile(new_content_path):
            print(f"MD Converting: {new_content_path}")
            generate_page(new_content_path, template_path, dest_path)
        else:
            generate_pages_recursive(os.path.join(curr_path, file), template_path)

def main():
    clear_public()
    static_to_public()
    generate_pages_recursive()
    
if __name__ == "__main__":
    main()