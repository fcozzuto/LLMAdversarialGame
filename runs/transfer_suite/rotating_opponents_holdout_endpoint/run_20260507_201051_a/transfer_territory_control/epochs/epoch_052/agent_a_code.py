def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    resources = observation.get("resources")
    if resources:
        target_list = [tuple(p) for p in resources]
    else:
        target_list = []
    unclaimed = observation.get("unclaimed_cells")
    if not target_list and unclaimed:
        target_list = [tuple(p) for p in unclaimed]
    if not target_list:
        target_list = [(ox, oy)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    self_pos = (sx, sy)
    opp_pos = (ox, oy)
    best = None
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        p = (nx, ny)
        tgt = min(target_list, key=lambda q: dist(p, q))
        d_t = dist(p, tgt)
        d_o = dist(p, opp_pos)
        val = (d_t, -d_o, 0 if (dx, dy) != (0, 0) else 1)
        if best is None or val < best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]