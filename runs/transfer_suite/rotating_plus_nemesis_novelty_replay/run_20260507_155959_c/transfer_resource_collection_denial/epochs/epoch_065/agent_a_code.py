def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        tx, ty = w // 2, h // 2
        best = (10**9, 10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if (dx == 0 and dy == 0) or (not inb(nx, ny)) or (nx, ny) in obs:
                    continue
                d = abs(nx - tx) + abs(ny - ty)
                if (d, abs(dx) + abs(dy), dx, dy) < (best[0], best[1], best[2], best[3]):
                    best = (d, abs(dx) + abs(dy), dx, dy)
        if best[0] == 10**9:
            return [0, 0]
        return [best[2], best[3]]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer resources where we are strictly closer than opponent; break ties by our closeness and corners/center bias.
    best_cell = None
    best_key = None
    for x, y in resources:
        sd = md(sx, sy, x, y)
        od = md(ox, oy, x, y)
        closer = od - sd
        # Small deterministic tie-breakers to reduce dithering:
        center_bias = -((x - (w - 1) / 2) ** 2 + (y - (h - 1) / 2) ** 2)
        key = (closer, -sd, center_bias, -(x + y), -x)
        if best_key is None or key > best_key:
            best_key = key
            best_cell = (x, y)

    tx, ty = best_cell
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                # Greedy: minimize distance to target, then maximize being ahead vs opponent.
                nd = md(nx, ny, tx, ty)
                opp_ahead = md(ox, oy, tx, ty) - nd
                moves.append((nd, -opp_ahead, abs(dx) + abs(dy), dx, dy))
    if not moves:
        return [0, 0]
    moves.sort()
    return [moves[0][3], moves[0][4]]