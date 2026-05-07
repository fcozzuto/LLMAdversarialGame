def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def bfs(st):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if st in obstacles:
            return dist
        x0, y0 = st
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                        if nd < dist[nx][ny]:
                            dist[nx][ny] = nd
                            q.append((nx, ny))
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    best_key = None
    for rx, ry in resources:
        ns = ds[rx][ry]
        no = do[rx][ry]
        if ns >= 10**9:
            continue
        # Prefer resources we can reach earlier; if tied, prefer closer to us and farther from opponent
        # Key: maximize (no-ns), then minimize ns, then deterministic tie on coords
        delta = no - ns
        key = (-delta, ns, rx, ry)  # using min for determinism
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry, delta, ns, no)

    if best is None:
        return [0, 0]

    tx, ty = best[0], best[1]

    # Move greedily toward target using ds, with obstacle safety
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            nd = ds[nx][ny]
            # Prefer smaller distance-to-target under our BFS; tie-break deterministically by coords
            cand.append((nd, rx := (nx - tx), ry := (ny - ty), dx, dy))
    if not cand:
        return [0, 0]
    cand.sort(key=lambda z: (abs(z[1]) + abs(z[2]), z[0], z[3], z[4]))
    return [int(cand[0][3]), int(cand[0][4])]