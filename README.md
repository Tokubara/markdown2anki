实现中参考了[这个repo](https://github.com/L-M-Sherlock/markdown2anki).

用法: `python3 md2tsv.py markdown文件路径 tsv路径`

##### 作用

本repo并不对一般的markdown适用(当然略作修改也可以, 但这不是它的目的), 它适用的是由ithoughtsx导出的markdown. 这样的markdown有严格的父子节点关系.

结果tsv有3个字段. 第一个字段是问题, 第二个字段是答案, 第三个字段是本repo的特点, 是父节点标题. 这样方便聚类.

