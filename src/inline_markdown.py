from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import ParentNode

import re

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    #split all nodes given some delimeter and text_type (ex. ** -. Text.BOLD)
    #splits only text nodes
    new_nodes = []
    for curr_node in old_nodes:
        if curr_node.text_type != TextType.TEXT:
            new_nodes.append(curr_node)
            continue
        split_text = curr_node.text.split(delimiter)
        if len(split_text) % 2 == 0:
            raise ValueError("Invalid markdown, formatted section not closed")
        for i in range(len(split_text)):
            if split_text[i] == "":
                continue
            if i % 2 == 0:
                new_nodes.append(TextNode(split_text[i], TextType.TEXT))
            else:
                new_nodes.append(TextNode(split_text[i], text_type))
    return new_nodes


def extract_markdown_images(text):
    reg_ex = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(reg_ex, text)

def extract_markdown_links(text):
    reg_ex = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(reg_ex, text)

def split_nodes_link(old_nodes):
    new_nodes = []
    for curr_node in old_nodes:
        if curr_node.text_type != TextType.TEXT:
            new_nodes.append(curr_node)
            continue
        all_links = extract_markdown_links(curr_node.text)
        if len(all_links) == 0:
            new_nodes.append(curr_node)
            continue
        leftover = curr_node.text
        for link in all_links:
            splits = leftover.split(f"[{link[0]}]({link[1]})", 1)
            if splits[0] != "":
                new_nodes.append(TextNode(splits[0], TextType.TEXT))
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            leftover = splits[1]
        if leftover != "":
            new_nodes.append(TextNode(splits[1], TextType.TEXT))
    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []
    for curr_node in old_nodes:
        if curr_node.text_type != TextType.TEXT:
            new_nodes.append(curr_node)
            continue
        all_images = extract_markdown_images(curr_node.text)
        if len(all_images) == 0:
            new_nodes.append(curr_node)
            continue
        leftover = curr_node.text
        for image in all_images:
            splits = leftover.split(f"![{image[0]}]({image[1]})", 1)
            if splits[0] != "":
                new_nodes.append(TextNode(splits[0], TextType.TEXT))
            new_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
            leftover = splits[1]
        if leftover != "":
            new_nodes.append(TextNode(leftover, TextType.TEXT))
    return new_nodes


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)


def block_to_html_node(block):
    block_type = block_to_block_type(block)
    if block_type == block_type_paragraph:
        return paragraph_to_html_node(block)
    if block_type == block_type_heading:
        return heading_to_html_node(block)
    if block_type == block_type_code:
        return code_to_html_node(block)
    if block_type == block_type_olist:
        return olist_to_html_node(block)
    if block_type == block_type_ulist:
        return ulist_to_html_node(block)
    if block_type == block_type_quote:
        return quote_to_html_node(block)
    raise ValueError("Invalid block type")


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(paragraph)
    return ParentNode("p", children)


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError(f"Invalid heading level: {level}")
    text = block[level + 1 :]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("Invalid code block")
    text = block[4:-3]
    children = text_to_children(text)
    code = ParentNode("code", children)
    return ParentNode("pre", [code])


def olist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[3:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)


def ulist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)


def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("Invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)