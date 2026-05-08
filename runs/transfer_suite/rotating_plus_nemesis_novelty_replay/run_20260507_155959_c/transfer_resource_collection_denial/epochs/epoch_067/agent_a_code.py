def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    env = observation.get("environment_name", "resource_collection")

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) != (sx, sy) and (nx, ny) not in obs:
                moves.append((dx, dy))
    moves.append((0, 0))
    moves = sorted(set(moves))

    if env != "resource_collection" or not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            val = (abs(nx - tx) + abs(ny - ty), abs(dx) + abs(dy), dx, dy)
            if best is None or val < best:
                best = val
        return [best[2], best[3]]

    # Choose target resource with best reach advantage (deterministic)
    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_target = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # Prefer we arrive earlier; otherwise prefer still-advantageous/closer
        advantage = ds - 0.8 * do
        val = (advantage, ds, do, rx, ry)
        if best_target is None or val < best_target[0]:
            best_target = (val, (rx, ry))
    if best_target is None:
        return [0, 0]

    tx, ty = best_target[1]

    # One-step lookahead: pick move that optimizes (reach objective + avoid worsening)
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ns = abs(tx - nx) + abs(ty - ny)
        no = abs(tx - ox) + abs(ty - oy)
        # If moving away too much, penalize; tie-break deterministically
        step_pen = (abs(nx - sx) + abs(ny - sy))
        val = (ns - 0.8 * no, ns, step_pen, dx, dy)
        if best_move is None or val < best_move[0]:
            best_move = (val, (dx, dy))

    return [best_move[1][0], best_move[1][1]]