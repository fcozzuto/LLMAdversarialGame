def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_res = None
    best_res_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; break ties by proximity and openness to corner risk.
        key = (-(do - ds), ds, (rx == 0 or rx == w - 1) + (ry == 0 or ry == h - 1))
        if best_res_key is None or key < best_res_key:
            best_res_key = key
            best_res = (rx, ry)

    rx, ry = best_res

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Evaluate each move against the chosen target: maximize reach advantage vs opponent.
    best = None
    best_val = None
    for dx, dy, nx, ny in moves:
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(ox, oy, rx, ry)
        val = (-(do2 - ds2), ds2)  # minimize ds2 and maximize (do2-ds2)
        # If advantage is tied, add a small deterministic nudge to avoid getting stuck near obstacles.
        openness = 0
        for tx in (-1, 0, 1):
            for ty in (-1, 0, 1):
                if tx == 0 and ty == 0:
                    continue
                px, py = nx + tx, ny + ty
                if 0 <= px < w and 0 <= py < h and (px, py) not in obstacles:
                    openness += 1
        val = (val[0], val[1], -openness)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]