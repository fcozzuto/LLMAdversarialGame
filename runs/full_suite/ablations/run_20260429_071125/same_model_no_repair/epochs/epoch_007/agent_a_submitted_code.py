def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs8 = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def bfs_dist(start):
        if not in_bounds(start[0], start[1]) or start in occ:
            return None
        dist = [[None] * h for _ in range(w)]
        q = [start]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs8:
                nx, ny = x + dx, y + dy
                if not in_bounds(nx, ny) or (nx, ny) in occ:
                    continue
                if dist[nx][ny] is None:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        return [0, 0]

    my_dist = bfs_dist((sx, sy))
    op_dist = bfs_dist((ox, oy))
    if my_dist is None:
        return [0, 0]
    if op_dist is None:
        op_dist = [[None] * h for _ in range(w)]

    def dget(dist, x, y):
        if dist is None:
            return None
        return dist[x][y]

    best = None
    best_key = None
    for rx, ry in resources:
        md = dget(my_dist, rx, ry)
        if md is None:
            continue
        od = dget(op_dist, rx, ry)
        if od is None:
            od = 10**9
        adv = od - md
        # Prefer bigger advantage; then quicker pickup; then nearer to center (stable tie-break).
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tie = ((rx - cx) ** 2 + (ry - cy) ** 2)
        key = (adv, -md, -tie)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    target_dist = bfs_dist((tx, ty))
    if target_dist is None:
        return [0, 0]

    curd = target_dist[sx][sy]
    if curd is None:
        return [0, 0]

    best_move = (0, 0)
    best_d = curd
    for dx, dy in dirs8 + [(0, 0)]:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in occ:
            continue
        nd = target_dist[nx][ny]
        if nd is None:
            continue
        # Deterministic: minimize distance to target; tie-break lexicographically by (dx, dy) via fixed order.
        if nd < best_d:
            best_d = nd
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]