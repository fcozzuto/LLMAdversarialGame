def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    best = (0, 0)
    best_score = -10**18

    if resources:
        tx, ty = min(resources, key=lambda p: (p[0] - sx) * (p[0] - sx) + (p[1] - sy) * (p[1] - sy))
    else:
        tx, ty = ox, oy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d2 = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        opp_d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = -d2 + 0.03 * opp_d2 - 0.35 * adj_obst(nx, ny)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]