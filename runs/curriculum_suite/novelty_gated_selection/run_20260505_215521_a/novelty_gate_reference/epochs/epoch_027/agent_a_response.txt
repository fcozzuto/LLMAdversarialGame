def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                targets.append((x, y))

    if targets:
        scored = []
        for (tx, ty) in targets:
            ds = md(sx, sy, tx, ty)
            do = md(ox, oy, tx, ty)
            advantage = do - ds  # positive means we get there first (in Manhattan)
            # Favor big advantage, then closer to us, and slight bias to edges to avoid opponent diagonal runs
            edge_bias = 1 if (tx in (0, w - 1) or ty in (0, h - 1)) else 0
            scored.append((-(advantage), ds - 0.3 * edge_bias, tx, ty))
        scored.sort()
        tx, ty = scored[0][2], scored[0][3]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ns = md(nx, ny, tx, ty)
        no = md(ox, oy, tx, ty)
        # If opponent can reach target sooner than we do after this move, deprioritize
        val = (ns - no, ns, abs((nx - tx) - (ny - ty)))  # tuple lexicographic
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]