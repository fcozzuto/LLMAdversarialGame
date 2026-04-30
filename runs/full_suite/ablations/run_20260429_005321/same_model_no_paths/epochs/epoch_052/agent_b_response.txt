def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def obs_adj_pen(x, y):
        # penalize getting boxed near obstacles
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h and (xx, yy) in obstacles:
                    pen += 2
        return pen

    # Pick a target where we have the largest distance advantage over opponent
    best = None
    best_delta = -10**9
    for rx, ry in resources:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        delta = dO - dS  # positive means we are closer
        if delta > best_delta or (delta == best_delta and (best is None or dS < cheb(sx, sy, best[0], best[1]))):
            best_delta = delta
            best = (rx, ry)
    tx, ty = best

    # Move evaluation: approach target, avoid walls/obstacles, and lightly avoid letting opponent get closer
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dT = cheb(nx, ny, tx, ty)
        dO = cheb(nx, ny, ox, oy)
        # Opponent "pressure" if they are closer to target after their next move (approx via current)
        dOppToT = cheb(ox, oy, tx, ty)
        # Encourage moves that keep us closer relative to opponent
        rel = dOppToT - dT
        val = 1000 * rel - 3 * dT + 0.6 * dO - obs_adj_pen(nx, ny)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move