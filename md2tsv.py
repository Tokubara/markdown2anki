#!/usr/bin/env python3 
import re
import sys
import os
import shutil
import argparse

# {{{1 用上的regex
sharps=r"^(##+)(?= )" # 这里的空格本意是与c的宏定义区分, 如果加了空格, c的宏定义的确可以解决, 但是python, bash之类的注释还是会有#, 而且也有空格, 于是规定标题级别至少为2. 因此, 真正导出的时候, 需要添加一个毫无意义的根节点. 解析时会跳过第一行, 也就是唯一的一级标题. 这样就能保证解析中不会遇到一级标题, 如果是`# `, 我们就可以保证它是注释, 是note_content的内容
sharps_pattern=re.compile(sharps)
math_formula=r"(?<!\$)\$([^$]+?)\$(?!\$)"
math_pattern=re.compile(math_formula)
bold_pattern=re.compile(r"\*\*(.*?)\*\*")
italic_pattern=re.compile(r"(?<!\*)\*([^*]+?)\*(?!\*)")
image_pattern=re.compile("!\[.+\]\((.+)\)")

# {{{1 preprocess
def preprocess(line):
    '''处理数学公式, 加粗'''
    line=line.strip()
    # $$替换为\(\)
    # line=re.sub(math_pattern, lambda match_obj:"\("+match_obj.group(1)+"\)", line)
    # 分开{{和}}(anki字段语法)
    line=line.replace('{{', '{ {')
    line=line.replace('}}', '} }')
    # ****替换为<b> </b>
    line=re.sub(bold_pattern, lambda match_obj:"<b>"+match_obj.group(1)+"</b>", line)
    # **替换为<i> </i>
    # line=re.sub(italic_pattern, lambda match_obj:"<i>"+match_obj.group(1)+"</i>", line)
    # 处理图片语法
    line=re.sub(image_pattern, lambda match_obj:"<img src=\""+os.path.split(match_obj.group(1))[-1]+"\">", line)
    # \n替换为<br>
    line=line+"<br>"
    
    return line

# {{{1 config变量
anki_media_path=r"/Users/quebec/Library/Application Support/Anki2/User 1/collection.media"

# {{{1 add_images
def add_images(line):
    '''对一行中出现的图片, 添加到media中, 没有则啥也不干, 不做文本上的替换处理'''
    img_path=re.match(image_pattern, line)
    if img_path is not None:
        img_path=img_path.group(1)        
        img_path=img_path.replace("%20"," ")
        # 如果是相对路径
        if not os.path.isabs(img_path):
            img_path=os.path.join(os.path.dirname(md_path),img_path)
        if not os.path.exists(img_path):
            print(f"{img_path} not exists")
        else:
            shutil.copy(img_path,anki_media_path)
            print(f"add image: {img_path}")

def add_card(title_level, level_titles, title_content, note_content, cards, recursive):
    assert title_level>1
    assert level_titles[title_level-1],f"title_content:{title_content}, note_content:{note_content}"
    if recursive:
        remark = ";".join(level_titles[2:title_level])
    else:
        remark = level_titles[title_level-1]
    new_card=title_content+"\t"+note_content+"\t"+remark+"\n" # remark就是表示Remark字段
    assert new_card.count("\t")==2 # 确保没有tab, 之所以如此, 是因为;非常常见, 在c代码中
    cards.append(new_card)

def md2tsv(md_path,output_path, recursive):
    level_titles=[0]*10 # 有点hash表的意思, level_titles[i]表示的是level为i的对应的最近的标题, 其中, level从1开始
    title_content=''
    note_content=''
    cards=[]
    # root_node=False # 如果已经遇到了

    # {{{1 解析markdown
    with open(md_path, 'r', encoding='UTF-8') as note_file:
        cards = []
        lines = note_file.readlines()
        for line in lines[1:]:
            # 空行情况不处理
            if line.strip() == '':
                continue
            elif re.match(sharps_pattern,line):
                # {{{3 标题先添加上一次的笔记, 因为遇到一个title意味着有一个新的笔记
                # 第一次除外
                if title_content and note_content:
                    add_card(title_level, level_titles, title_content, note_content, cards, recursive)
                    note_content=''
                # 先获得标题等级
                title_level=len(re.match(sharps_pattern,line).group(1))
                title_content = re.sub(sharps_pattern, "", line).strip()
                level_titles[title_level] = title_content
            else: 
                note_content=note_content+preprocess(line)

        if title_content and note_content:
            add_card(title_level, level_titles, title_content, note_content, cards, recursive)

    # {{{1 写入文件
    with open(output_path, 'w', encoding='UTF-8') as output_file:
        output_file.writelines(cards)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="convert markdown exported by ithoughtsx to tsv which can be imported to anki Basic Notes(Front, Back, Remark)")
    parser.add_argument('md_path', type=str, help='path of markdown file', nargs="?", default="/Users/quebec/Desktop/tmp.markdown")
    parser.add_argument('output_path', type=str, help='path of result tsv file', nargs="?", default="/Users/quebec/Desktop/anki.tsv")
    parser.add_argument("-r", dest="recursive", help="Remark add all ancestors", action="store_true", default=False)
    args = parser.parse_args()
    md2tsv(args.md_path, args.output_path, args.recursive)
