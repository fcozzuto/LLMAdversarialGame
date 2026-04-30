def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not valid(sx, sy):
        sx, sy = max(0, min(w - 1, sx)), max(0, min(h - 1, sy))

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources I can reach much sooner than opponent; otherwise fall back to closest.
        key = (-(do - ds), ds, rx, ry)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key
    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dself = cheb(nx, ny, tx, ty)
            # If there is an obstacle nearby, avoid steps that move closer to it.
            mind_obs = 10**9
            for (ox2, oy2) in obstacles:
                t = cheb(nx, ny, ox2, oy2)
                if t < mind_obs:
                    mind_obs = t
            # Tie-break deterministically by move order.
            moves.append((dself, -mind_obs, dx, dy))

    # Deterministic choice: minimize dself, then maximize obstacle clearance, then lexicographic move.
    moves.sort()
    return [int(moves[0][2]), int(moves[0][3])]