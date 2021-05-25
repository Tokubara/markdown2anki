实现中参考了[这个repo](https://github.com/L-M-Sherlock/markdown2anki).

用法: 见`python3 md2tsv.py -h`

注意, 由于笔记中可能出现python, bash等代码, 可能有行以`# `开始, 为了处理这种情况, 我跳过了markdown第一行(ithoughtx导出的第一行一定会是一级标题), 为了在使用-r选项不丢失一级标题信息, 需要在真正的根节点前面再加一个父节点, 这样真正的根节点就是2级标题开始的.

##### 作用

本repo并不对一般的markdown适用(当然略作修改也可以, 但这不是它的目的), 它适用的是由ithoughtsx导出的markdown. 这样的markdown有严格的父子节点关系.

结果tsv有3个字段. 第一个字段是问题, 第二个字段是答案, 第三个字段是本repo的特点, 是父节点标题. 这样方便聚类.

