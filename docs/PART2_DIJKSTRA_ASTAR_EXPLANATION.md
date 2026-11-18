# 📘 Part 2 Presentation & Viva Guide: Greedy & Heuristic Pathfinding (Dijkstra & A* Search)

> **Presenter:** Chaitanya Patil  
> **Course:** Data Structures & Algorithms (DSA) / Design & Analysis of Algorithms (DAA)  
> **Topic:** Shortest Path Algorithms, Binary Min-Heap Priority Queues, Spatial Haversine Heuristic & Complexity Analysis

---

## 📂 1. Files Owned & Code Locations

You are responsible for explaining the following **4 core files** in the repository:

| File Name | Exact Path | Lines | What it does |
|---|---|---|---|
| **`Dijkstra.h`** | [`src/core/Dijkstra.h`](file:///c:/Users/Asus/pune-bus-route-optimizer/src/core/Dijkstra.h) | 1–12 | Class declaration and static `findShortestPath()` method interface |
| **`Dijkstra.cpp`** | [`src/core/Dijkstra.cpp`](file:///c:/Users/Asus/pune-bus-route-optimizer/src/core/Dijkstra.cpp) | 1–136 | Dijkstra implementation using `std::priority_queue` min-heap and edge relaxation |
| **`AStar.h`** | [`src/core/AStar.h`](file:///c:/Users/Asus/pune-bus-route-optimizer/src/core/AStar.h) | 1–12 | Class declaration and static `findShortestPath()` method interface |
| **`AStar.cpp`** | [`src/core/AStar.cpp`](file:///c:/Users/Asus/pune-bus-route-optimizer/src/core/AStar.cpp) | 1–155 | A* Search using admissible Haversine distance heuristic $h(n)$ and $f(n) = g(n) + h(n)$ |
| *(Supporting)* | [`src/core/Graph.cpp`](file:///c:/Users/Asus/pune-bus-route-optimizer/src/core/Graph.cpp#L12-L24) | 12–24 | `Graph::haversineDistance()` mathematical formula implementation |

---

## 🧠 2. Core Concepts: What You Are Explaining to Mam

### 1. Dijkstra’s Algorithm (Greedy Strategy)
- **Paradigm:** **Greedy Approach**. At every step, it makes the locally optimal choice — it picks the unvisited node with the smallest tentative distance from the source, trusting that it will lead to a globally optimal shortest path.
- **Why Greedy Works Here:** Because all road edge weights are non-negative ($w(u,v) \ge 0$). Once a node is extracted from the min-heap and marked `visited`, its shortest distance is finalized and will never be improved.

### 2. A* Search Algorithm (Informed / Heuristic Search)
- **Paradigm:** **Informed Search**. Unlike Dijkstra which searches blindly in all directions equally (like a ripple in water), A* uses geographic domain knowledge to guide the search toward the target stop.
- **Evaluation Function:**
  $$f(n) = g(n) + h(n)$$
  - $g(n)$: The exact cost incurred from the start node to current node $n$.
  - $h(n)$: The estimated heuristic cost from node $n$ to the target destination.
  - $f(n)$: Total estimated cost of the path going through node $n$.

### 3. The Haversine Spatial Heuristic ($h(n)$)
- In road navigation, Earth is a sphere ($R = 6371\text{ km}$). The straight-line spherical distance between GPS coordinates $(\text{lat}_1, \text{lon}_1)$ and $(\text{lat}_2, \text{lon}_2)$ is the **Haversine Distance**:
  $$a = \sin^2\left(\frac{\Delta \text{lat}}{2}\right) + \cos(\text{lat}_1)\cos(\text{lat}_2)\sin^2\left(\frac{\Delta \text{lon}}{2}\right)$$
  $$c = 2 \cdot \text{atan2}(\sqrt{a}, \sqrt{1-a})$$
  $$\text{Distance} = R \cdot c$$

### 4. Mathematical Proof of Admissibility
- **Admissibility Condition:** A heuristic $h(n)$ is admissible if it never overestimates the true remaining cost to the goal:
  $$h(n) \le h^*(n) \quad (\text{where } h^*(n) \text{ is true actual road cost})$$
- **Why Haversine is Admissible:** The great-circle distance is the shortest possible physical distance between two points on the surface of a sphere. Any real-world bus route traverses physical roads, curves, and turns, meaning the actual road distance $D_{\text{road}} \ge D_{\text{haversine}}$ always.
- **What about Fastest-Time Mode?**
  In our code (`AStar.cpp`, lines 40–44), when optimizing for travel time, we compute:
  $$h_{\text{time}}(n) = \frac{\text{Haversine Distance}}{v_{\max}} \times 60 \text{ minutes}$$
  where $v_{\max}$ is the fastest free-flow highway speed on the entire network (`graph.maxFreeFlowSpeedKmph()`). Since no bus can travel faster than $v_{\max}$, this time estimate can never overestimate the remaining time. Hence, **it remains 100% admissible!**

---

## 💻 3. Line-by-Line Code Walkthrough

When Mam asks: *"Show me your code for Dijkstra and A*"*, open these files and explain these exact blocks:

---

### A. Dijkstra Code Walkthrough (`src/core/Dijkstra.cpp`)

#### Block 1: Min-Heap & State Containers (Lines 36–49)
```cpp
// 1. Min-heap priority queue storing pair<distance, stop_id>
// std::greater sorts elements so the smallest distance is always at top()
using Element = std::pair<double, std::string>;
std::priority_queue<Element, std::vector<Element>, std::greater<Element>> pq;

std::unordered_map<std::string, double> distances; // Stores tentative distances
std::unordered_map<std::string, std::string> previous; // Parent pointers to reconstruct path
std::unordered_map<std::string, bool> visited; // Closed set so we never reprocess a node

for (const auto& id : graph.getAllStopIds()) {
    distances[id] = std::numeric_limits<double>::infinity();
    visited[id] = false;
}
distances[source_id] = 0.0;
pq.push({0.0, source_id});
```
> **What to explain to Mam:**  
> *"Mam, we initialize all node distances to infinity ($\infty$) and source to 0. We use `std::greater<Element>` in `std::priority_queue` to create a Min-Heap. In C++, the default priority queue is a Max-Heap, so `std::greater` ensures we extract the minimum distance node in $\mathcal{O}(\log V)$ time."*

#### Block 2: The Greedy Exploration & Relaxation Loop (Lines 56–82)
```cpp
while (!pq.empty()) {
    auto [current_dist, u] = pq.top();
    pq.pop();

    if (visited[u]) continue; // Skip if already visited
    visited[u] = true;
    nodes_explored++;

    if (u == target_id) { // Early exit once destination is popped!
        target_reached = true;
        break;
    }

    // Edge Relaxation for all neighbors
    for (const auto& edge : graph.getOutgoingEdges(u)) {
        const std::string& v = edge.target_id;
        double weight = edge.cost(by_time); // km or minutes

        if (distances[u] + weight < distances[v]) {
            distances[v] = distances[u] + weight;
            previous[v] = u; // Record parent
            pq.push({distances[v], v});
            edge_relaxations++;
        }
    }
}
```
> **What to explain to Mam:**  
> *"Here is the relaxation condition: `if (distances[u] + weight < distances[v])`. If going through stop `u` gives a shorter path to neighbor `v`, we update `distances[v]`, record `u` as `previous[v]`, and push the new distance into the min-heap."*

#### Block 3: Path Reconstruction (Lines 95–107)
```cpp
std::vector<std::string> path;
std::string curr = target_id;
while (!curr.empty()) {
    path.push_back(curr);
    if (curr == source_id) break;
    curr = previous[curr];
}
std::reverse(path.begin(), path.end());
```
> **What to explain to Mam:**  
> *"Once target is reached, we backtrack from `target_id` to `source_id` using our `previous` map, and reverse the vector to get the forward route from start to finish."*

---

### B. A* Search Code Walkthrough (`src/core/AStar.cpp`)

#### Block 1: The Heuristic Lambda (Lines 40–44)
```cpp
const double max_speed_kmph = graph.maxFreeFlowSpeedKmph();
auto heuristic = [&](const Stop* s) {
    double km = Graph::haversineDistance(s->lat, s->lon, target_stop->lat, target_stop->lon);
    return by_time ? (km / max_speed_kmph * 60.0) : km;
};
```
> **What to explain to Mam:**  
> *"This lambda computes the Haversine straight-line distance from current stop `s` to `target_stop`. If we are optimizing for travel time, we divide by the maximum possible speed on the network so that $h(n)$ is expressed in minutes without ever overestimating."*

#### Block 2: $f(n) = g(n) + h(n)$ Evaluation Loop (Lines 73–102)
```cpp
while (!open_set.empty()) {
    auto [current_f, u] = open_set.top(); // Node with smallest f_score
    open_set.pop();

    if (closed_set[u]) continue;
    closed_set[u] = true;
    nodes_explored++;

    if (u == target_id) break;

    for (const auto& edge : graph.getOutgoingEdges(u)) {
        const std::string& v = edge.target_id;
        if (closed_set[v]) continue;

        double tentative_g = g_score[u] + edge.cost(by_time);

        if (tentative_g < g_score[v]) {
            previous[v] = u;
            g_score[v] = tentative_g;
            double h = heuristic(graph.getStop(v));
            f_score[v] = tentative_g + h; // f(n) = g(n) + h(n)
            open_set.push({f_score[v], v});
            edge_relaxations++;
        }
    }
}
```
> **What to explain to Mam:**  
> *"In Dijkstra, the priority queue is sorted purely on `g_score` (distance from start). In A\*, the priority queue is sorted on `f_score = tentative_g + h`. This pulls the search directionally toward the target instead of expanding radially in all directions."*

---

## 📊 4. Complexity Analysis Table

| Metric | Dijkstra's Algorithm | A* Search Algorithm |
|---|---|---|
| **Algorithmic Paradigm** | **Greedy** | **Informed / Heuristic** |
| **Data Structure** | Binary Min-Heap (`std::priority_queue`) | Binary Min-Heap (`std::priority_queue`) |
| **Worst-Case Time** | $\mathcal{O}((V + E) \log V)$ | $\mathcal{O}((V + E) \log V)$ |
| **Practical Exploration** | Explores all directions radially (**24 nodes**) | Directionally pruned (**16 nodes** on Swargate ➔ Hinjewadi) |
| **Auxiliary Space** | $\mathcal{O}(V)$ for `distances`, `visited`, `previous` | $\mathcal{O}(V)$ for `g_score`, `f_score`, `closed_set`, `previous` |
| **Negative Edge Handling** | ❌ Fails (Requires Bellman-Ford) | ❌ Fails |

---

## 🎙️ 5. Your 2-Minute Spoken Script (Rehearse This!)

> *"Good morning / afternoon Mam. I am **Chaitanya Patil**, and I will explain the **Greedy and Heuristic Pathfinding Engine** of our transit router.*
>
> *In our project, we implemented two primary routing algorithms: **Dijkstra's Algorithm** and **A\* Search**, located in `src/core/Dijkstra.cpp` and `src/core/AStar.cpp`.*
>
> *First, for Dijkstra, we use the **Greedy paradigm**. We maintain a Min-Heap using `std::priority_queue` with `std::greater`. At each step, we extract the unvisited stop with the minimum tentative distance. Because our road distances are strictly positive, extracting the minimum node guarantees that its distance is permanently optimal. The time complexity is $\mathcal{O}((V+E)\log V)$ where $V = 24$ hubs and $E = 38$ corridors.*
>
> *Second, we asked: **Can we make search faster by using GPS coordinates?** That is why we implemented **A\* Search**.*  
> *A\* evaluates nodes using $f(n) = g(n) + h(n)$. While $g(n)$ is the exact distance traveled from the origin, $h(n)$ is our **Haversine Distance Heuristic**, implemented in `Graph.cpp` line 12. It computes the spherical straight-line distance to the target.*
>
> *Because straight-line distance on a sphere is the shortest physical path, actual road distance is always greater than or equal to $h(n)$. This satisfies the mathematical condition of **Admissibility** ($h(n) \le \text{TrueCost}$), guaranteeing that A\* always finds the true shortest path.*
>
> *Let me demonstrate the power of A\* right now on our live system:*
> *(Click GUI or run CLI)*:  
> *When routing from **Swargate to Hinjewadi Phase 3**:*  
> *- **Dijkstra** explores **24 nodes** and relaxes 34 edges.*  
> *- **A\*** explores only **16 nodes** — a **33% reduction in search space** while producing the exact same 26.40 km optimal route!*
>
> *Now my teammate Divya will explain how we handle negative edges and dynamic programming with Bellman-Ford."*

---

## ❓ 6. Top 8 Tough Viva Questions & Perfect Answers

#### Q1. Why did you use `std::greater` in your `std::priority_queue`?
> **Answer:**  
> *"By default in C++, `std::priority_queue<T>` is a Max-Heap (it uses `std::less<T>` and puts the largest element on top). For Dijkstra and A\*, we need a Min-Heap to extract the minimum cost node in $\mathcal{O}(1)$ inspection and $\mathcal{O}(\log V)$ extraction. Specifying `std::greater<std::pair<double, std::string>>` reverses the comparator to create a Min-Heap."*

#### Q2. Can Dijkstra handle negative edge weights? Why or why not?
> **Answer:**  
> *"No, Dijkstra cannot handle negative edge weights. Dijkstra greedily marks a node as visited and assumes its shortest distance is finalized. If a negative edge appears later in the graph, it could shorten the path to an already visited node, but Dijkstra will never re-evaluate it. For negative weights, we use the Bellman-Ford algorithm implemented by Divya in `BellmanFord.cpp`."*

#### Q3. What is the difference between an Admissible heuristic and a Consistent (Monotonic) heuristic?
> **Answer:**  
> *"An **admissible** heuristic never overestimates the cost to reach the goal ($h(n) \le h^*(n)$). A **consistent (or monotonic)** heuristic satisfies the triangle inequality: for every node $n$ and neighbor $n'$, $h(n) \le c(n, n') + h(n')$. Because great-circle spherical distance strictly obeys the triangle inequality on Earth, our Haversine heuristic is both admissible and consistent. This guarantees no closed node ever needs to be re-opened."*

#### Q4. What happens if $h(n) = 0$ for all nodes in A*?
> **Answer:**  
> *"If $h(n) = 0$, then $f(n) = g(n) + 0 = g(n)$. The evaluation function degenerates purely to the distance from start, which means **A\* becomes mathematically identical to standard Dijkstra's algorithm**."*

#### Q5. What happens if $h(n)$ overestimates the true cost?
> **Answer:**  
> *"If $h(n)$ overestimates the true cost, the heuristic is no longer admissible. A\* will still run and find a path, but it is **no longer guaranteed to find the optimal shortest path**; it might return a suboptimal route because it unfairly penalized a node on the true shortest path."*

#### Q6. What is the time complexity of Dijkstra with an Adjacency Matrix vs a Binary Heap?
> **Answer:**  
> *- With an **Adjacency Matrix and linear scan array**: $\mathcal{O}(V^2)$.*  
> *- With an **Adjacency List and Binary Min-Heap (`std::priority_queue`)**: $\mathcal{O}((V + E) \log V)$.*  
> *For our Pune transit network, the binary heap is significantly faster and uses less memory.*

#### Q7. In your code, you have `if (visited[u]) continue;`. Why is that line necessary if you use a priority queue?
> **Answer:**  
> *"In standard C++ `std::priority_queue`, there is no `decreaseKey()` operation. When we find a shorter distance to node `v`, we push a duplicate pair `(new_dist, v)` into the heap. The old, larger distance pair remains in the heap. When the old pair is eventually popped later, `if (visited[u]) continue;` skips it in $\mathcal{O}(1)$ time without doing redundant edge relaxations. This technique is called **Lazy Deletion**."*

#### Q8. How did you adapt A* when routing by travel time (with traffic) instead of distance?
> **Answer:**  
> *"In `src/core/AStar.cpp` line 40, when `by_time = true`, edge costs are in minutes. To keep $h(n)$ admissible, we take the Haversine distance in kilometers and divide it by `graph.maxFreeFlowSpeedKmph()` (the maximum possible speed on any corridor in the network) and multiply by 60. Since no bus can exceed the maximum free-flow speed, $h_{\text{time}}(n)$ will never overestimate the time required to reach the destination."*

---

## 🖥️ 7. Live Terminal Commands to Run During Demo

Keep this ready in your PowerShell terminal to show Mam:

```powershell
# 1. Run Dijkstra only
./run_cli.sh --from swargate --to hinjewadi_ph3 --algo dijkstra

# 2. Run A* only
./run_cli.sh --from swargate --to hinjewadi_ph3 --algo astar

# 3. Side-by-side comparison proof (Dijkstra vs A* vs Bellman-Ford)
./run_cli.sh --from swargate --to hinjewadi_ph3 --compare
```
*(In the output table, point your finger at the **Nodes Explored** column: 24 for Dijkstra vs 16 for A\*!)*
