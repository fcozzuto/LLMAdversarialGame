def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))[:2]
    ox, oy = observation.get("opponent_position", (0, 0))[:2]

    obst = observation.get("obstacles") or []
    obstacles = set()
    for p in obst:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []

    def cell_list(arr):
        out = []
        for p in arr:
            if p and len(p) >= 2:
                out.append((p[0], p[1]))
        return out

    targets = cell_list(unclaimed)
    if not targets:
        targets = cell_list(resources)
    if not targets:
        ot = observation.get("opponent_territory") or []
        targets = cell_list(ot)
    if not targets:
        targets = [(ox, oy)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_adj = man((sx, sy), (ox, oy)) == 1

    best_t = None
    best_td = 10**9
    for t in targets:
        d = man((sx, sy), t)
        if d < best_td:
            best_td = d
            best_t = t
    if best_t is None:
        return [0, 0]

    best_move = [0, 0]
    best_val = -10**18

    tx, ty = best_t
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = man((nx, ny), (tx, ty))
        adj_to_opp = man((nx, ny), (ox, oy)) == 1
        val = -d - (200 if adj_to_opp else 0) - (3 if (dx == 0 and dy == 0 and not opp_adj) else 0)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move