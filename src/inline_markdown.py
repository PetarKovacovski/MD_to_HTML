from textnode import TextNode, TextType
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

#text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
#print(text_to_textnodes(text))