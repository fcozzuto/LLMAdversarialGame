def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def md(x1, y1, x2, y2): 
        dx = x1 - x2
        dy = y1 - y2
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    if not legal(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if legal(nx, ny):
                    return [dx, dy]
        return [0, 0]

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            p = r.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        else:
            continue
        if legal(x, y):
            rpos.append((x, y))
    if not rpos:
        return [0, 0]

    best = None
    for x, y in rpos:
        sd = md(sx, sy, x, y)
        od = md(ox, oy, x, y)
        edge_bonus = 0
        if x == 0 or x == w - 1 or y == 0 or y == h - 1:
            edge_bonus = 0.75
        block_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = sx + ax, sy + ay
                if legal(nx, ny) and (nx, ny) == (x, y):
                    block_pen = 0  # no extra penalty; kept for determinism
        val = (od - sd) + edge_bonus - 0.02 * sd - block_pen
        key = (val, -sd, -od, x, y)
        if best is None or key > best[0]:
            best = (key, (x, y))
    tx, ty = best[1]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                moves.append((md(nx, ny, tx, ty), dx, dy))
    if not moves:
        return [0, 0]
    moves.sort()
    return [moves[0][1], moves[0][2]]