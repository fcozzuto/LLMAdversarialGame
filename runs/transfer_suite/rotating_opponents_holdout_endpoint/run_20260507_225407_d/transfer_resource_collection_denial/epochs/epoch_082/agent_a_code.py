def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_key = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        key = (do - ds, -ds)  # prefer where we are closer than opponent; then closer overall
        if best_key is None or key > best_key:
            best_key, best = key, (rx, ry)

    tx, ty = best
    best_move = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_to_t = md(nx, ny, tx, ty)
        d_to_o = md(nx, ny, ox, oy)
        val = ( -d_to_t, d_to_o, -abs(dy), -abs(dx) )  # minimize distance to target; keep away from opponent; deterministic tie breaks
        if best_val is None or val > best_val:
            best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]