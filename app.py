import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from explainer import DEFAULT_MODEL, explain_algorithm

load_dotenv(Path(__file__).with_name('.env'))

EXAMPLES = {
    'Search: Binary search': '''def binary_search(values, target):
    low, high = 0, len(values) - 1
    while low <= high:
        middle = (low + high) // 2
        if values[middle] == target:
            return middle
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1''',
    'Search: Linear search': '''def linear_search(values, target):
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1''',
    'Sorting: Merge sort': '''def merge_sort(values):
    if len(values) <= 1:
        return values
    middle = len(values) // 2
    left = merge_sort(values[:middle])
    right = merge_sort(values[middle:])
    return merge(left, right)''',
    'Sorting: Bubble sort': '''def bubble_sort(values):
    values = values.copy()
    for end in range(len(values) - 1, 0, -1):
        swapped = False
        for index in range(end):
            if values[index] > values[index + 1]:
                values[index], values[index + 1] = values[index + 1], values[index]
                swapped = True
        if not swapped:
            break
    return values''',
    'Sorting: Insertion sort': '''def insertion_sort(values):
    values = values.copy()
    for index in range(1, len(values)):
        current = values[index]
        position = index - 1
        while position >= 0 and values[position] > current:
            values[position + 1] = values[position]
            position -= 1
        values[position + 1] = current
    return values''',
    'Sorting: Quick sort': '''def quick_sort(values):
    if len(values) < 2:
        return values
    pivot = values[len(values) // 2]
    lower = [value for value in values if value < pivot]
    equal = [value for value in values if value == pivot]
    higher = [value for value in values if value > pivot]
    return quick_sort(lower) + equal + quick_sort(higher)''',
    'Graphs: Breadth-first search': '''from collections import deque

def breadth_first_search(graph, start):
    visited = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return visited''',
    'Graphs: Depth-first search': '''def depth_first_search(graph, start):
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        stack.extend(reversed(graph[node]))
    return visited''',
    'Graphs: Dijkstra shortest paths': '''import heapq

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    queue = [(0, start)]
    while queue:
        distance, node = heapq.heappop(queue)
        if distance != distances[node]:
            continue
        for neighbor, weight in graph[node]:
            candidate = distance + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                heapq.heappush(queue, (candidate, neighbor))
    return distances''',
    'Graphs: Topological sort': '''from collections import deque

def topological_sort(graph):
    indegree = {node: 0 for node in graph}
    for neighbors in graph.values():
        for neighbor in neighbors:
            indegree[neighbor] += 1
    queue = deque(node for node, degree in indegree.items() if degree == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)
    if len(order) != len(graph):
        raise ValueError('Graph contains a cycle')
    return order''',
    'Dynamic programming: Fibonacci': '''def fibonacci(number, memo=None):
    if memo is None:
        memo = {0: 0, 1: 1}
    if number not in memo:
        memo[number] = fibonacci(number - 1, memo) + fibonacci(number - 2, memo)
    return memo[number]''',
    'Dynamic programming: 0/1 knapsack': '''def knapsack(weights, values, capacity):
    best = [0] * (capacity + 1)
    for weight, value in zip(weights, values):
        for limit in range(capacity, weight - 1, -1):
            best[limit] = max(best[limit], best[limit - weight] + value)
    return best[capacity]''',
    'Greedy: Activity selection': '''def select_activities(activities):
    selected = []
    for start, finish in sorted(activities, key=lambda activity: activity[1]):
        if not selected or start >= selected[-1][1]:
            selected.append((start, finish))
    return selected''',
    'Trees: Inorder traversal': '''def inorder(node):
    if node is None:
        return []
    return inorder(node.left) + [node.value] + inorder(node.right)''',
    'Strings: KMP pattern search': '''def build_lps(pattern):
    lps = [0] * len(pattern)
    length = 0
    index = 1
    while index < len(pattern):
        if pattern[index] == pattern[length]:
            length += 1
            lps[index] = length
            index += 1
        elif length:
            length = lps[length - 1]
        else:
            index += 1
    return lps

def kmp_search(text, pattern):
    if not pattern:
        return 0
    lps = build_lps(pattern)
    text_index = pattern_index = 0
    while text_index < len(text):
        if text[text_index] == pattern[pattern_index]:
            text_index += 1
            pattern_index += 1
            if pattern_index == len(pattern):
                return text_index - pattern_index
        elif pattern_index:
            pattern_index = lps[pattern_index - 1]
        else:
            text_index += 1
    return -1''',
    'Number theory: Euclidean GCD': '''def gcd(first, second):
    while second:
        first, second = second, first % second
    return abs(first)''',
    'Search: Jump search': '''from math import isqrt

def jump_search(values, target):
    length = len(values)
    step = isqrt(length) or 1
    start = 0
    while start < length and values[min(start + step, length) - 1] < target:
        start += step
    for index in range(start, min(start + step, length)):
        if values[index] == target:
            return index
    return -1''',
    'Search: Interpolation search': '''def interpolation_search(values, target):
    low, high = 0, len(values) - 1
    while low <= high and values[low] <= target <= values[high]:
        if values[low] == values[high]:
            return low if values[low] == target else -1
        position = low + (target - values[low]) * (high - low) // (values[high] - values[low])
        if values[position] == target:
            return position
        if values[position] < target:
            low = position + 1
        else:
            high = position - 1
    return -1''',
    'Search: Exponential search': '''def exponential_search(values, target):
    if not values:
        return -1
    bound = 1
    while bound < len(values) and values[bound] < target:
        bound *= 2
    low, high = bound // 2, min(bound, len(values) - 1)
    while low <= high:
        middle = (low + high) // 2
        if values[middle] == target:
            return middle
        if values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1''',
    'Sorting: Selection sort': '''def selection_sort(values):
    values = values.copy()
    for start in range(len(values)):
        smallest = min(range(start, len(values)), key=values.__getitem__)
        values[start], values[smallest] = values[smallest], values[start]
    return values''',
    'Sorting: Heap sort': '''def heap_sort(values):
    values = values.copy()
    length = len(values)

    def sift_down(root, end):
        while 2 * root + 1 < end:
            child = 2 * root + 1
            if child + 1 < end and values[child] < values[child + 1]:
                child += 1
            if values[root] >= values[child]:
                return
            values[root], values[child] = values[child], values[root]
            root = child

    for root in range(length // 2 - 1, -1, -1):
        sift_down(root, length)
    for end in range(length - 1, 0, -1):
        values[0], values[end] = values[end], values[0]
        sift_down(0, end)
    return values''',
    'Sorting: Counting sort': '''def counting_sort(values):
    if not values:
        return []
    smallest, largest = min(values), max(values)
    counts = [0] * (largest - smallest + 1)
    for value in values:
        counts[value - smallest] += 1
    result = []
    for offset, count in enumerate(counts):
        result.extend([smallest + offset] * count)
    return result''',
    'Sorting: Radix sort': '''def radix_sort(values):
    if any(value < 0 for value in values):
        raise ValueError('Radix sort example expects non-negative integers')
    result = values.copy()
    place = 1
    largest = max(result, default=0)
    while largest // place:
        buckets = [[] for _ in range(10)]
        for value in result:
            buckets[(value // place) % 10].append(value)
        result = [value for bucket in buckets for value in bucket]
        place *= 10
    return result''',
    'Sorting: Shell sort': '''def shell_sort(values):
    values = values.copy()
    gap = len(values) // 2
    while gap:
        for index in range(gap, len(values)):
            current = values[index]
            position = index
            while position >= gap and values[position - gap] > current:
                values[position] = values[position - gap]
                position -= gap
            values[position] = current
        gap //= 2
    return values''',
    'Graphs: Bellman-Ford': '''def bellman_ford(nodes, edges, start):
    distances = {node: float('inf') for node in nodes}
    distances[start] = 0
    for _ in range(len(nodes) - 1):
        changed = False
        for source, target, weight in edges:
            if distances[source] != float('inf') and distances[source] + weight < distances[target]:
                distances[target] = distances[source] + weight
                changed = True
        if not changed:
            break
    has_negative_cycle = any(
        distances[source] != float('inf') and distances[source] + weight < distances[target]
        for source, target, weight in edges
    )
    return distances, has_negative_cycle''',
    'Graphs: Floyd-Warshall': '''def floyd_warshall(distances):
    distances = [row.copy() for row in distances]
    for middle in range(len(distances)):
        for source in range(len(distances)):
            for target in range(len(distances)):
                distances[source][target] = min(
                    distances[source][target],
                    distances[source][middle] + distances[middle][target],
                )
    return distances''',
    'Graphs: Prim minimum spanning tree': '''import heapq

def prim_mst(graph, start):
    visited = {start}
    edges = [(weight, start, neighbor) for neighbor, weight in graph[start]]
    heapq.heapify(edges)
    tree = []
    while edges and len(visited) < len(graph):
        weight, source, target = heapq.heappop(edges)
        if target in visited:
            continue
        visited.add(target)
        tree.append((source, target, weight))
        for neighbor, next_weight in graph[target]:
            if neighbor not in visited:
                heapq.heappush(edges, (next_weight, target, neighbor))
    return tree''',
    'Graphs: Kruskal minimum spanning tree': '''def kruskal_mst(nodes, edges):
    parent = {node: node for node in nodes}

    def find(node):
        if parent[node] != node:
            parent[node] = find(parent[node])
        return parent[node]

    tree = []
    for weight, first, second in sorted(edges):
        root_first, root_second = find(first), find(second)
        if root_first != root_second:
            parent[root_first] = root_second
            tree.append((first, second, weight))
    return tree''',
    'Graphs: A-star pathfinding': '''import heapq

def a_star(graph, start, goal, heuristic):
    queue = [(heuristic[start], 0, start)]
    previous = {start: None}
    cost = {start: 0}
    while queue:
        _, current_cost, node = heapq.heappop(queue)
        if node == goal:
            path = []
            while node is not None:
                path.append(node)
                node = previous[node]
            return path[::-1]
        if current_cost != cost[node]:
            continue
        for neighbor, weight in graph[node]:
            candidate = current_cost + weight
            if candidate < cost.get(neighbor, float('inf')):
                cost[neighbor] = candidate
                previous[neighbor] = node
                heapq.heappush(queue, (candidate + heuristic[neighbor], candidate, neighbor))
    return []''',
    'Dynamic programming: Longest common subsequence': '''def lcs_length(first, second):
    table = [[0] * (len(second) + 1) for _ in range(len(first) + 1)]
    for row in range(1, len(first) + 1):
        for column in range(1, len(second) + 1):
            if first[row - 1] == second[column - 1]:
                table[row][column] = table[row - 1][column - 1] + 1
            else:
                table[row][column] = max(table[row - 1][column], table[row][column - 1])
    return table[-1][-1]''',
    'Dynamic programming: Coin change': '''def minimum_coins(coins, amount):
    best = [0] + [float('inf')] * amount
    for total in range(1, amount + 1):
        for coin in coins:
            if coin <= total:
                best[total] = min(best[total], best[total - coin] + 1)
    return best[amount] if best[amount] != float('inf') else -1''',
    'Dynamic programming: Edit distance': '''def edit_distance(first, second):
    previous = list(range(len(second) + 1))
    for row, first_char in enumerate(first, start=1):
        current = [row]
        for column, second_char in enumerate(second, start=1):
            insert = current[column - 1] + 1
            delete = previous[column] + 1
            replace = previous[column - 1] + (first_char != second_char)
            current.append(min(insert, delete, replace))
        previous = current
    return previous[-1]''',
    'Dynamic programming: Longest increasing subsequence': '''from bisect import bisect_left

def lis_length(values):
    tails = []
    for value in values:
        position = bisect_left(tails, value)
        if position == len(tails):
            tails.append(value)
        else:
            tails[position] = value
    return len(tails)''',
    'Greedy: Fractional knapsack': '''def fractional_knapsack(items, capacity):
    total_value = 0
    for value, weight in sorted(items, key=lambda item: item[0] / item[1], reverse=True):
        if capacity <= 0:
            break
        taken = min(capacity, weight)
        total_value += taken * value / weight
        capacity -= taken
    return total_value''',
    'Greedy: Minimum meeting rooms': '''def minimum_meeting_rooms(intervals):
    events = []
    for start, end in intervals:
        events.extend([(start, 1), (end, -1)])
    active = maximum = 0
    for _, change in sorted(events):
        active += change
        maximum = max(maximum, active)
    return maximum''',
    'Trees: Preorder traversal': '''def preorder(node):
    if node is None:
        return []
    return [node.value] + preorder(node.left) + preorder(node.right)''',
    'Trees: Postorder traversal': '''def postorder(node):
    if node is None:
        return []
    return postorder(node.left) + postorder(node.right) + [node.value]''',
    'Trees: Level-order traversal': '''from collections import deque

def level_order(root):
    if root is None:
        return []
    values = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        values.append(node.value)
        if node.left is not None:
            queue.append(node.left)
        if node.right is not None:
            queue.append(node.right)
    return values''',
    'Trees: Binary search tree lookup': '''def bst_search(node, target):
    while node is not None and node.value != target:
        node = node.left if target < node.value else node.right
    return node''',
    'Strings: Naive pattern search': '''def find_pattern(text, pattern):
    for start in range(len(text) - len(pattern) + 1):
        if text[start:start + len(pattern)] == pattern:
            return start
    return 0 if not pattern else -1''',
    'Strings: Rabin-Karp search': '''def rabin_karp(text, pattern):
    if not pattern:
        return 0
    base, modulus = 256, 1_000_000_007
    pattern_hash = text_hash = 0
    highest = pow(base, len(pattern) - 1, modulus)
    for char in pattern:
        pattern_hash = (pattern_hash * base + ord(char)) % modulus
    for index, char in enumerate(text):
        text_hash = (text_hash * base + ord(char)) % modulus
        if index >= len(pattern):
            text_hash = (text_hash - ord(text[index - len(pattern)]) * highest) % modulus
        if index >= len(pattern) - 1 and text_hash == pattern_hash:
            start = index - len(pattern) + 1
            if text[start:start + len(pattern)] == pattern:
                return start
    return -1''',
    'Strings: Palindrome check': '''def is_palindrome(text):
    left, right = 0, len(text) - 1
    while left < right:
        if text[left] != text[right]:
            return False
        left += 1
        right -= 1
    return True''',
    'Number theory: Sieve of Eratosthenes': '''def sieve(limit):
    is_prime = [True] * (limit + 1)
    if limit >= 0:
        is_prime[0] = False
    if limit >= 1:
        is_prime[1] = False
    for number in range(2, int(limit ** 0.5) + 1):
        if is_prime[number]:
            for multiple in range(number * number, limit + 1, number):
                is_prime[multiple] = False
    return [number for number, prime in enumerate(is_prime) if prime]''',
    'Number theory: Primality test': '''def is_prime(number):
    if number < 2:
        return False
    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 1
    return True''',
    'Number theory: Fast exponentiation': '''def fast_power(base, exponent, modulus=None):
    result = 1
    if modulus is not None:
        base %= modulus
    while exponent > 0:
        if exponent % 2:
            result *= base
            if modulus is not None:
                result %= modulus
        base *= base
        if modulus is not None:
            base %= modulus
        exponent //= 2
    return result''',
    'Backtracking: N-Queens': '''def solve_n_queens(size):
    solutions = []
    columns, descending, ascending = set(), set(), set()
    placement = []

    def place(row):
        if row == size:
            solutions.append(placement.copy())
            return
        for column in range(size):
            if column in columns or row - column in descending or row + column in ascending:
                continue
            columns.add(column)
            descending.add(row - column)
            ascending.add(row + column)
            placement.append(column)
            place(row + 1)
            placement.pop()
            columns.remove(column)
            descending.remove(row - column)
            ascending.remove(row + column)

    place(0)
    return solutions''',
    'Backtracking: Subsets': '''def all_subsets(values):
    result = []

    def build(index, subset):
        if index == len(values):
            result.append(subset.copy())
            return
        build(index + 1, subset)
        subset.append(values[index])
        build(index + 1, subset)
        subset.pop()

    build(0, [])
    return result''',
    'Backtracking: Permutations': '''def permutations(values):
    result, current, used = [], [], [False] * len(values)

    def build():
        if len(current) == len(values):
            result.append(current.copy())
            return
        for index, value in enumerate(values):
            if used[index]:
                continue
            used[index] = True
            current.append(value)
            build()
            current.pop()
            used[index] = False

    build()
    return result''',
    'Backtracking: Maze path': '''def find_maze_path(maze, start, goal):
    rows, columns = len(maze), len(maze[0])
    path, visited = [], set()

    def search(row, column):
        position = (row, column)
        if not (0 <= row < rows and 0 <= column < columns):
            return False
        if maze[row][column] == 1 or position in visited:
            return False
        path.append(position)
        if position == goal:
            return True
        visited.add(position)
        for row_step, column_step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if search(row + row_step, column + column_step):
                return True
        path.pop()
        return False

    return path if search(*start) else []''',
    'Backtracking: Sudoku solver': '''def solve_sudoku(board):
    empty = next(((row, col) for row in range(9) for col in range(9) if board[row][col] == 0), None)
    if empty is None:
        return True
    row, col = empty
    for value in range(1, 10):
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        if value in board[row]:
            continue
        if any(board[index][col] == value for index in range(9)):
            continue
        if any(board[r][c] == value for r in range(box_row, box_row + 3) for c in range(box_col, box_col + 3)):
            continue
        board[row][col] = value
        if solve_sudoku(board):
            return True
        board[row][col] = 0
    return False''',
}
DATASET_PATH = Path(__file__).parent / 'data' / 'ai4i2020.csv'


@st.cache_data
def load_dataset() -> pd.DataFrame:
    return pd.read_csv(DATASET_PATH)


def clear_workspace() -> None:
    st.session_state['algorithm_text'] = ''
    st.session_state.pop('explanation', None)
    st.session_state.pop('explanation_error', None)


st.set_page_config(page_title='AI Algorithm Explainer', page_icon='A', layout='wide')
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Space+Grotesk:wght@500;600;700&display=swap');
        :root { --ink: #172522; --muted: #53645e; --line: #d7e0da; --paper: #f4f7f3; --panel: #ffffff; --green: #276b54; --orange: #bd582f; }
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: var(--ink); }
        .stApp, [data-testid="stAppViewContainer"] { background: var(--paper); color: var(--ink); }
        .block-container { max-width: 1380px; padding: 2rem 2.5rem 3rem; }
        h1, h2, h3 { color: var(--ink); font-family: 'Space Grotesk', sans-serif; letter-spacing: 0; }
        .eyebrow { color: var(--orange); font-family: 'IBM Plex Mono', monospace; font-size: .78rem; font-weight: 500; text-transform: uppercase; }
        .app-title { color: var(--ink); font-family: 'Space Grotesk', sans-serif; font-size: 2.7rem; font-weight: 700; line-height: 1.12; margin: .35rem 0 .45rem; }
        .app-meta { color: var(--muted); font-size: .92rem; margin-bottom: 1.5rem; }
        .pane-title { border-bottom: 1px solid var(--line); color: var(--ink); font-family: 'Space Grotesk', sans-serif; font-size: 1.15rem; font-weight: 600; margin: .3rem 0 1rem; padding-bottom: .7rem; }
        .stTextArea textarea { background: var(--panel); border: 1px solid #b9c9c0; border-radius: 8px; color: var(--ink); font-family: 'IBM Plex Mono', monospace; font-size: .87rem; line-height: 1.55; }
        .stTextArea textarea:focus { border-color: var(--green); box-shadow: 0 0 0 1px var(--green); }
        .stSelectbox label, .stTextArea label { color: var(--ink) !important; font-weight: 600; }
        .stButton > button { border-radius: 6px; font-weight: 600; min-height: 2.7rem; }
        .stButton > button[kind="primary"] { background: var(--green); border-color: var(--green); }
        .stButton > button[kind="primary"]:hover { background: #1e5744; border-color: #1e5744; }
        [data-testid="stExpander"] { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; }
        [data-testid="stMarkdownContainer"] code { font-family: 'IBM Plex Mono', monospace; }
        .stAlert { border-radius: 7px; }
        @media (max-width: 700px) { .block-container { padding: 1.25rem 1rem 2rem; } .app-title { font-size: 2.15rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="eyebrow">Computer science learning tool</div>', unsafe_allow_html=True)
st.markdown('<div class="app-title">AI Algorithm Explainer</div>', unsafe_allow_html=True)
model = os.getenv('HUGGINGFACE_MODEL', DEFAULT_MODEL).strip() or DEFAULT_MODEL
st.markdown(
    f'<div class="app-meta">Hugging Face Inference Providers · automatic provider selection · {model}</div>',
    unsafe_allow_html=True,
)

st.session_state.setdefault('algorithm_text', EXAMPLES['Search: Binary search'])
left, right = st.columns([0.92, 1.08], gap='large')
with left:
    st.markdown('<div class="pane-title">Algorithm input</div>', unsafe_allow_html=True)
    example_name = st.selectbox('Load an example', list(EXAMPLES))
    load_column, clear_column = st.columns(2)
    with load_column:
        if st.button('Load example', use_container_width=True):
            st.session_state['algorithm_text'] = EXAMPLES[example_name]
            st.session_state.pop('explanation', None)
            st.rerun()
    with clear_column:
        st.button('Clear', on_click=clear_workspace, use_container_width=True)

    source_text = st.text_area(
        'Algorithm name, pseudocode, or code',
        key='algorithm_text',
        height=340,
        label_visibility='collapsed',
        placeholder='Paste an algorithm name, pseudocode, or implementation...',
    )
    explain_clicked = st.button('Explain algorithm', type='primary', use_container_width=True)

    if explain_clicked:
        try:
            with st.spinner('Generating explanation with Hugging Face...'):
                st.session_state['explanation'] = explain_algorithm(
                    source_text,
                    os.getenv('HUGGINGFACE_API_KEY') or os.getenv('HF_TOKEN', ''),
                    model,
                )
            st.session_state.pop('explanation_error', None)
        except ValueError as exc:
            st.session_state['explanation_error'] = str(exc)
            st.session_state.pop('explanation', None)

with right:
    st.markdown('<div class="pane-title">Explanation</div>', unsafe_allow_html=True)
    if st.session_state.get('explanation_error'):
        st.error(st.session_state['explanation_error'])
    elif st.session_state.get('explanation'):
        st.markdown(st.session_state['explanation'])
    else:
        st.caption('No explanation generated yet.')

st.caption('Submitted code is analyzed as text and is never executed.')

st.markdown('---')
st.markdown('## AI4I 2020 predictive maintenance dataset')
dataset = load_dataset()
machine_failures = int(dataset['Machine failure'].sum())
total_machines = len(dataset)
metric_columns = st.columns(3)
metric_columns[0].metric('Machine records', f'{total_machines:,}')
metric_columns[1].metric('Features', f'{dataset.shape[1]}')
metric_columns[2].metric('Machine failures', f'{machine_failures:,}', f'{machine_failures / total_machines:.1%} of records')
st.dataframe(dataset, width='stretch', hide_index=True, height=480)
