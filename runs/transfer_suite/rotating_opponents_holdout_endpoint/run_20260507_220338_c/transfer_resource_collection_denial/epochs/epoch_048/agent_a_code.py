def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = [tuple(p) for p in (observation.get("resources", []) or []) if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx >= dy else dy

    def pick_target():
        best = None
        best_score = -10**18
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach first; lightly prefer not racing same-row as opponent.
            row_pen = 6 if ry == oy else 0
            score = (opd - myd) * 100 - row_pen - myd
            if score > best_score:
                best_score = score
                best = (rx, ry)
        return best

    tx, ty = pick_target()

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # Evaluate candidate moves by the best achievable "advantage" after moving one step.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        v = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            row_pen = 6 if ry == oy else 0
            score = (opd - myd) * 100 - row_pen - myd
            if score > v:
                v = score
        # Small deterministic bias toward moving closer to chosen target.
        v += -(cheb(nx, ny, tx, ty))
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]