import javalang
import os
import re
import xml.etree.ElementTree as ET

from pathlib import Path

from config import PROJECT_ROOT_DIR

def is_getter(method):
    """判断方法是否为 Getter"""
    # 1. 名字以 get 开头
    if not method.name.startswith('get'):
        return False
    # 2. 没有参数
    if len(method.parameters) != 0:
        return False
    # 3. 返回值不是 void
    if method.return_type == 'void':
        return False
    return True

def is_setter(method):
    """判断方法是否为 Setter"""
    # 1. 名字以 set 开头
    if not method.name.startswith('set'):
        return False
    # 2. 只有一个参数
    if len(method.parameters) != 1:
        return False
    return True
# 判断是否 get set开头的业务方法，业务方法需要单元测试
def getter_setter_field(method) -> str:
	if not method or not method.name:
	    return None
	method_name = method.name
	if (method_name.startswith('get')):
		method_name = method_name.replace("get", "")
	if (method_name.startswith('set')):
		method_name = method_name.replace("set", "")
	return method_name[0].lower() + method_name[1:]


# 分析 java 文件
def is_skip_java_file(java_file_path:str) -> bool:
    # javalang 对最新版本的java 解析有问题
    
    class_name = "UNKNOWN"
    p = Path(java_file_path)
    class_name = p.stem
    class_type = "ClassDeclaration"
    try:
        with open(java_file_path, 'r', encoding='utf-8') as file:
            # 读取文件内容
            source_code = file.read()
            # 解析为抽象语法树
        tree = javalang.parse.parse(source_code)
        # 遍历解析树中的所有类型定义
        # 一个Java文件可能包含多个类/接口定义
        class_declaration = tree.types[0]
        class_name = class_declaration.name
        class_type = class_declaration.__class__.__name__
        if (class_type in ["AnnotationDeclaration", "EnumDeclaration", "InterfaceDeclaration"]):
            return True
        if (len(class_declaration.methods) == 0):
        	return True
        # print(len(class_declaration.methods))
        method_count = 0
        fields = []
        for field in class_declaration.fields:
            # field.declarators 是 VariableDeclarator 列表，通常取第一个
            if field.declarators:
                field_name = field.declarators[0].name
                fields.append(field_name)
        
        for method in class_declaration.methods:
            # methods.append(method.name)
            # print(method.name)
            
            if is_getter(method) or is_setter(method):
                field = getter_setter_field(method)
                if field in fields:
                    continue
            method_count += 1
            # if ( class_name == "AbstractRouteHandlerMapping"):
            #     print("method:" + method) 
        if method_count == 0:
            return True
        return False
    except Exception as e:
        return False

# 查找 src/main/java 下的源代码文件
def find_java_files(base_dir: str) -> list[Path]:
    java_file_dir = str(PROJECT_ROOT_DIR) + "/" + base_dir
    """
    查找 Maven 项目中的所有 Java 源文件
    Args:
        base_dir: 项目根目录或指定的模块目录
    Returns:
        Java 文件路径列表
    """
    java_files = []
    base_path = Path(java_file_dir)

    skip_classes = ["AnnotationDeclaration", "EnumDeclaration", "InterfaceDeclaration"]

    # 查找所有 src/main/java 目录
    for src_dir in base_path.rglob('src/main/java'):
        for java_file in src_dir.rglob('*.java'):
            if (is_skip_java_file(java_file)):
                continue
            java_files.append(str(java_file).replace(str(PROJECT_ROOT_DIR) + "/", ""))
            
    return java_files


def find_maven_modules(base_dir: str) -> list[str]:
    """
    查找 Maven 项目的所有模块

    Args:
        base_dir: 项目根目录

    Returns:
        模块目录列表
    """
    modules = []
    base_path = Path(base_dir)

    # 查找根 pom.xml
    root_pom = base_path / 'pom.xml'
    if root_pom.exists():
        modules.append(str(root_pom))

    # 查找子模块
    for pom_file in base_path.rglob('pom.xml'):
        if pom_file != root_pom:
            modules.append(str(pom_file))
    code_modules = []
    for pom in modules:
        if not is_pom_packaging(pom):
            code_modules.append(Path(pom).parent)
    result = []
    for module in code_modules:
        result.append(str(module).replace(str(PROJECT_ROOT_DIR) + "/", ""))
    return list(result)


# 判断 maven 的 pom.xml 是否包含 ` <packaging>pom</packaging> `
def is_pom_packaging(pom_path: str) -> bool:
    """
    判断 Maven 项目的 pom.xml 中 <packaging> 是否为 pom

    :param pom_path: pom.xml 文件路径
    :return: 如果 packaging 为 pom 返回 True，否则返回 False
    """
    # 定义命名空间（Maven POM 的标准命名空间）
    namespaces = {'pom': 'http://maven.apache.org/POM/4.0.0'}

    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()

        # 查找 packaging 元素（注意使用命名空间前缀）
        packaging_elem = root.find('pom:packaging', namespaces)

        # 如果元素不存在，默认 packaging 为 jar
        if packaging_elem is None:
            return False

        # 判断元素文本是否为 'pom'
        return packaging_elem.text == 'pom'

    except (ET.ParseError, FileNotFoundError, IOError) as e:
        print(f"读取或解析 {pom_path} 时出错: {e}")
        return False


