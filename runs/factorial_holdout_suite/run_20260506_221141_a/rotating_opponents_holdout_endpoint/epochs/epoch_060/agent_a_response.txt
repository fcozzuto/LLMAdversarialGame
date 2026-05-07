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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose best target by relative closeness (self first), deterministic tie-break.
    best_r = None
    best_val = None
    for r in resources:
        rx, ry = r
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Reward being closer than opponent; penalize being farther.
        val = (-ds * 10) + (0 if do >= ds else (do - ds) * 2) + (do - ds)
        key = (val, -ds, -do, rx, ry)
        if best_val is None or key > best_val:
            best_val = key
            best_r = r

    tx, ty = best_r

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny):
                dist = cheb(nx, ny, tx, ty)
                moves.append((dist, dx, dy))
    if not moves:
        return [0, 0]

    moves.sort(key=lambda t: (t[0], t[1], t[2]))
    return [moves[0][1], moves[0][2]]