def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best_moves = []

    if resources:
        # Pick target that we can reach quickly and that is relatively far for opponent.
        best_t, best_sc = None, None
        for tx, ty in resources:
            ds = man(sx, sy, tx, ty)
            do = man(ox, oy, tx, ty)
            edge = 1 if (tx in (0, w - 1) or ty in (0, h - 1)) else 0
            sc = ds * 10 - do * 6 + edge * 2
            if best_sc is None or sc < best_sc:
                best_sc, best_t = sc, (tx, ty)
        tx, ty = best_t
    else:
        # No visible resources: steer toward opponent corner quadrant (deterministic).
        tx, ty = (w - 1, h - 1) if (ox + oy) > (sx + sy) else (0, 0)

    # Choose move minimizing projected "target race" score after move, avoiding obstacles.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = man(nx, ny, tx, ty)
        do2 = man(ox, oy, tx, ty)
        edge = 1 if (tx in (0, w - 1) or ty in (0, h - 1)) else 0
        sc2 = ds2 * 10 - do2 * 6 + edge * 2
        # Small penalty for moving away from opponent to reduce diagonal probing effectiveness.
        sc2 += (man(nx, ny, ox, oy) - man(sx, sy, ox, oy))
        if best_score is None or sc2 < best_score:
            best_score = sc2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]