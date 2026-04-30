def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            resources.append((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obstacles)
    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gain = do - ds
            # Prefer resources we can reach at least as fast, then maximize gain, then closer.
            cand = (-(1 if gain >= 0 else 0), -gain, ds, rx, ry)
            if best is None or cand < best[0]:
                best = (cand, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1, h - 1) if (sx + sy) % 2 == 0 else (0, 0)

    # One-step: among valid moves, choose minimizing distance to target; tie-break deterministically.
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): 
            continue
        d = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        # Encourage stealing: after move, prioritize if we don't get worse relative to opponent.
        rel = cheb(nx, ny, tx, ty) - (oppd - cheb(ox, oy, tx, ty) + 0)
        key = (d, -rel, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]