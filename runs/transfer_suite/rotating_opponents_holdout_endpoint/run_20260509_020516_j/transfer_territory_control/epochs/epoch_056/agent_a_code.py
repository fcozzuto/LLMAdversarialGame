def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_set(v):
        s = set()
        for p in v or []:
            if p is None or len(p) < 2:
                continue
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                s.add((x, y))
        return s

    obstacles = to_set(observation.get("obstacles"))
    resources = to_set(observation.get("resources"))
    unclaimed = to_set(observation.get("unclaimed_cells"))

    dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1),(0,0)]

    def inb(x, y): return 0 <= x < W and 0 <= y < H
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def md(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    targets = resources if resources else (unclaimed if unclaimed else {(ox, oy)})
    best = None
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = min(md((nx, ny), t) for t in targets) if targets else 10**9
        # Tie-break: prefer moving away from opponent if resources are absent
        opp = md((nx, ny), (ox, oy))
        # Tie-break: prefer cells with more free neighbors
        neigh = 0
        for kx, ky in [(-1,0),(1,0),(0,-1),(0,1)]:
            tx, ty = nx + kx, ny + ky
            if free(tx, ty):
                neigh += 1
        key = (d, -neigh if not resources else neigh, -opp if not resources else opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return list(best) if best is not None else [0, 0]