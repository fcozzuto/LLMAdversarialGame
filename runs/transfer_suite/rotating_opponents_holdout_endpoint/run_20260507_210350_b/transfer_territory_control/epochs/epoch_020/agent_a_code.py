def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in observation.get(key, []) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    unclaimed = list(to_set("unclaimed_cells"))
    if resources:
        tx, ty = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy) + (p[0] == ox and p[1] == oy))
    elif unclaimed:
        tx, ty = min(unclaimed, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
    else:
        tx, ty = w // 2, h // 2

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = abs(nx - tx) + abs(ny - ty)
        avoid = -1 if (nx, ny) == (ox, oy) else 0
        opp_dist = abs(nx - ox) + abs(ny - oy)
        score = d * 10 - opp_dist + avoid
        if best is None or score < best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [best[0], best[1]]