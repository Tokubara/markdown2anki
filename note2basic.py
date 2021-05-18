import re
import sys
import os
import shutil

# {{{1 用上的regex
sharps=r"^(##+)(?= )" # 空格是必须的, 因为c有宏定义
sharps_pattern=re.compile(sharps)
math_formula=r"(?<!\$)\$([^$]+?)\$(?!\$)"
math_pattern=re.compile(math_formula)
bold_pattern=re.compile(r"\*\*(.*?)\*\*")
italic_pattern=re.compile(r"(?<!\*)\*([^*]+?)\*(?!\*)")
image_pattern=re.compile("!\[.+\]\((.+)\)")

# {{{1 preprocess
def preprocess(line): # TODO
    '''处理数学公式, 加粗'''
    line=line.strip()
    # $$替换为\(\)
    line=re.sub(math_pattern, lambda match_obj:"\("+match_obj.group(1)+"\)", line)
    # 分开{{和}}(anki字段语法)
    line=line.replace('{{', '{ {')
    line=line.replace('}}', '} }')
    # ****替换为<b> </b>
    line=re.sub(bold_pattern, lambda match_obj:"<b>"+match_obj.group(1)+"</b>", line)
    # **替换为<i> </i>
    line=re.sub(italic_pattern, lambda match_obj:"<i>"+match_obj.group(1)+"</i>", line)
    # 处理图片语法
    line=re.sub(image_pattern, lambda match_obj:"<img src=\""+os.path.split(match_obj.group(1))[-1]+"\">", line)
    # \n替换为<br>
    line=line.replace("\n","<br>")
    
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

def md2tsv(md_path,output_path):
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
                    assert title_level>1,line
                    assert level_titles[title_level-1],title_content+" "+note_content
                    new_card=title_content+"\t"+note_content+"\t"+level_titles[title_level-1]+"\n"
                    assert new_card.count("\t")==2
                    cards.append(new_card) # TODO 加入expandtab处理, 确保没有tab, 之所以如此, 是因为;非常常见, 在c代码中
                    note_content=''
                # 先获得标题等级
                title_level=len(re.match(sharps_pattern,line).group(1))
                title_content = re.sub(sharps_pattern, "", line).strip()
                level_titles[title_level] = title_content
            else: 
                note_content=note_content+preprocess(line)

        if title_content and note_content:
            assert title_level>1
            assert level_titles[title_level-1]
            cards.append(title_content+"\t"+note_content+"\t"+level_titles[title_level-1]+"\n") # TODO 加入expandtab处理, 确保没有tab, 之所以如此, 是因为;非常常见, 在c代码中

    # {{{1 写入文件
    with open(output_path, 'w', encoding='UTF-8') as output_file: # TODO 加入命令行参数
        output_file.writelines(cards)

if __name__ == "__main__":
    md2tsv(*sys.argv[1:])
