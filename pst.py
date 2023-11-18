import graphviz
import numpy as np

class Node:
    """
    Класс узла дерева PST
    
    Атрибуты:
    parent - ссылка на объект родительского узла
    name - имя узла
    level - уровень узла (0 - root)
    children - словарь дочерних объектов 
            {<объект>: [<количество объектов>, <вероятность перехода>]}
    has_children - флаг того, что у узла есть дочерние объекты

    Методы:
    add_child - добавить дочерний узел
    get_child_by_name - получить дочерний узел по имени
    get_node_distance - вычислить расстояние до другого узла
    show_info - показать информацию об узле
    add_digraph_node - добавить узел для визуализации
    """

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.level = parent.level+1 if parent else 0
        self.children = {}
        self.has_children = False

    def add_child(self, node):
        """
        Добавление дочернего узла и подсчет кол-ва дочерних узлов
        """
        child = self.get_child_by_name(node.name)
        self.has_children = True

        if child:
            self.children[child]['count'] += 1
            return child

        else:
            self.children[node] = {'count': 1}
            return node

    def get_child_by_name(self, name):
        """
        Возвращает дочерний элемент по имени, если не существует - None
        """
        for child in self.children:
            if child.name == name:
                return child
        
        return None

    def get_node_distance(self, node):    
        """
        Возвращает расстояние между узлами на основании распределения
        вероятностей дочерних объектов:
        - если дочерний объект присутствует в обоих узлах: (p1-p2)**2
        - если дочерний объект отсутствует - p1**2,
        где p1 и p2 - вероятности появления дочернего объекта в исходном
        и сравниваемом узла соответственно
        """
        if not self.has_children:
            return 0

        distance = 0
        
        for child1, info1 in self.children.items():
            if node == None:
                distance += info1['p']**2
                
            elif child1.name in [c.name for c in node.children.keys()]:
                info2 = node.children[node.get_child_by_name(child1.name)]
                distance += (info1['p'] - info2['p'])**2
                
            else:
                distance += info1['p']**2

        return distance
        
    
    def show_info(self):
        childrens = {node.name:cnt for node,cnt in self.children.items()}
        childrens = childrens if len(childrens) else 'No (LEAF)'
        parent = self.parent.name if self.parent else 'No (ROOT)'

        
        print(f"""name: {self.name}, level: L{self}, parent: {parent}, children: {childrens}""")

    def add_digraph_node(self, digraph):
        digraph.node(str(self), self.name)
        
        if len(self.children) > 0:
            for node, info in self.children.items():
                digraph.node(str(node), node.name)
                digraph.edge(str(self), str(node), label=f"{info['p']:.2f}", penwidth=str(info['p']*4))
                
        return digraph

class PST:
    """
    Класс дерева PST
    
    Атрибуты:
    root - ссылка на объект родительского узла
    name - имя родительского узла
    depth - глубина дерева (по сути длина инициализирующей цепочки)
    power - количество элементов, на которых училось дерево
    has_children - флаг того, что у узла есть дочерние объекты

    Методы:
    add_subchain - добавить обучающую цепочку
    evaluate_probability - вычислить вероятности переходов
    evaluate_node_probability - рекурсия для вычисления вероятностей
    show_tree_info - показать информацию о дереве
    show_node_info - рекурсия для вывода информации о дереве
    plot_PST_graph - нарисовать граф дерева
    add_PST_node_to_digraph - добавление узла в граф дерева
    get_distance - вычислить расстояние между деревьями
    get_node_distance - рекурсия для вычисления расстояния между деревьями
    """
    
    def __init__(self, init_chain):
        self.root = Node(parent = None, name = init_chain[0])
        self.name = self.root.name
        self.depth = len(init_chain)
        self.power = 0 # мощность дерева (кол-во элементов, на которых училось)

        node = self.root      

        for element in init_chain[1:]:
            new_node = Node(parent = node, name = element)
            node.add_child(new_node)
            node = new_node

    def add_subchain(self, subchain):
        """
        добавление обучающей последовательности в дерево
        """
        node = self.root

        for element in subchain[1:]:
            node = node.add_child(Node(parent = node, name = element))
            
        self.power += 1

    def evaluate_probability(self):
        """
        Вычисление вероятности перехода на основании счетчиков объектов
        """
        self.evaluate_node_probability(self.root)

    def evaluate_node_probability(self, node):
        """
        Рекурсия для прохода по всем узлам и вычисления их вероятности
        """
        
        if len(node.children) == 0:
            return

        cnt_sum = sum(i['count'] for i in node.children.values())
        for child in node.children:
            node.children[child]['p'] = node.children[child]['count']/cnt_sum
            self.evaluate_node_probability(child)        

    def show_tree_info(self):
        """
        Вывод информации о дереве
        """
        self.show_node_info(self.root)

    def show_node_info(self, node):
        """
        Рекурсия для прохода по всем узлам и вывода информации по ним
        """
        
        info = node.show_info()
        
        if len(node.children) == 0:
            return

        for child in node.children:
            self.show_node_info(child)

    def plot_PST_graph(self):
        """
        отрисовка дерева в виде графа
        """
        f = graphviz.Digraph(f'PST graph {id(self)}')
        f = self.add_PST_node_to_digraph(node = self.root, digraph = f)
        
        f.view()
        return f

    def add_PST_node_to_digraph(self, node, digraph):
        """
        Рекурсия для прохода по всем узлам и добавления в граф для отрисовки
        """        
        digraph = node.add_digraph_node(digraph)
        
        if len(node.children) == 0:
            return

        for child in node.children:
            self.add_PST_node_to_digraph(child, digraph)

        return digraph

    def get_distance(self, pst):    
        """
        получение расстояния между деревьями на основании
        вероятностей переходов между их узлами
        """

        return self.get_node_distance(self.root, pst.root)

    def get_node_distance(self, node1, node2, distance=0, debug=False):
        """
        Рекурсия для прохода по всем узлам и подсчета расстояний между ними
        """        
        if not node1.has_children:
            return distance

        
        distance += node1.get_node_distance(node2)

        if debug:
            
            try:
                print(f"{node1.name}-{node1.level}, {node2.name}-{node2.level}: {distance}")
    
            except:
                print(f"{node1.name}-{node1.level}, ---: {distance}")   
        
        
        for child1 in node1.children:
            if node2 == None:
                distance = self.get_node_distance(child1, None, distance)
                
            elif child1.name in [c.name for c in node2.children]:
                child2 = node2.get_child_by_name(child1.name)
                distance = self.get_node_distance(child1, child2, distance)
                
            else:
                distance = self.get_node_distance(child1, None, distance)

        return distance
        
class PST_model:
    """
    Класс, описывающий последовательность событий
    при помощи PST деревьев
    
    Атрибуты:
    trees - список PST деревьев данного класса
    _depth - глубина дерева (по сути длина инициализирующей цепочки)


    Методы:
    fit - обучение деревьев на выбранной последовательности
    get_PST_by_name - получение объекта класса PST по его имени из списка деревьев модели
    get_event_prob - вычисление вероятностей переходов по всем деревьям модели
    _get_subchains - получение последовательностей нужной длины для обучения деревьев
    """
    
    def __init__(self, depth: int):
        self._depth = depth
        self.trees = []
    
    def fit(self, chain):
        """
        Обучение класса на заданной последовательности:
        вся последовательность делится на подпоследовательности заданной длины,
        после чего в каждой подпоследовательности первый элемент объявляется 
        корневым элементом и события последовательности добавляются в соответствующее дерево
        Если ранее дерево не было создано, создается новое дерево
        """
        
        for subchain in self._get_subchains(chain):

            if self.get_PST_by_name(subchain[0]):
                self.get_PST_by_name(subchain[0]).add_subchain(subchain)

            else:
                new_pst = PST(subchain)
                self.trees.append(new_pst)   

        for tree in self.trees:
            tree.evaluate_probability()
    
    def get_PST_by_name(self, name):
        """
        Возвращает дерево по имени из списка деревьев модели
        """
        for tree in self.trees:
            if tree.name == name:
                return tree
        
        return None

    def get_event_prob(self, subchain):
        """
        вычисляет вероятности переходов на основании кол-ва дочерних объектов 
        для каждого узла каждого дерева
        """
        if len(subchain) != self._depth:
            print(f"Chain lenght must be equal {self._depth}")

            return None

        pst = self.get_PST_by_name(subchain[0])
        if pst:
            node = pst.root
            prob = 1
            for element in subchain[1:]:
                child = node.get_child_by_name(element)

                if child == None:
                    return 0
                else:
                    prob *= node.children[child]['p']
                    
                node = child

            return prob
                
        else:
            print(f"There are no PST with fisrt event id = {subchain[0]}")   
            return 0

    def get_chain_prob(self, chain):
        result = [np.NaN]*self._depth

        for subchain in self._get_subchains(chain):
            result.append(self.get_event_prob(subchain))

        return result

    def _get_subchains(self, chain):
        """
        получение подпоследовательностей установленной длины из заданной последовательности
        """
        subchains = []

        for i in range(len(chain) - self._depth):
            subchains.append(chain[i:i+self._depth])

        return subchains