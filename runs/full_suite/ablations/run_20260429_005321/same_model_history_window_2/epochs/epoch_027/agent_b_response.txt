def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    # If no visible resources, drift to corner farthest from opponent (deterministic).
    if not resources:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, tx, ty)
            if best is None or v < best_val or (v == best_val and (dx, dy) < best):
                best, best_val = (dx, dy), v
        if best is None:
            return [0, 0]
        return [int(best[0]), int(best[1])]

    # Choose target resource: likely earliest considering opponent proximity.
    tx, ty = min(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]) + 0.5 * cheb(ox, oy, r[0], r[1]), r[0], r[1]))

    # Evaluate one-step moves by minimizing distance to target while keeping distance from opponent.
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_to_o = cheb(nx, ny, ox, oy)
        # Strongly prefer approaching target; lightly prefer moving away from opponent.
        # Also mildly avoid adjacency to obstacles by penalizing moves that touch obstacle cells.
        obst_adj = 0
        for adx, ady in moves:
            if (nx + adx, ny + ady) in obst:
                obst_adj += 1
        v = d_to_t * 10 - d_to_o + obst_adj * 0.25
        if best is None or v < best_val or (v == best_val and (dx, dy) < best):
            best, best_val = (dx, dy), v

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]