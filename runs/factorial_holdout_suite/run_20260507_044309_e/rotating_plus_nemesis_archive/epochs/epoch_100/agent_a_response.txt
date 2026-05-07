def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_cell = (sx, sy)
    best_val = -10**9

    if resources:
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            # Assume nemesis tends to sweep along rows/axes: penalize using Manhattan for opponent.
            od = manh(ox, oy, rx, ry)
            # If resource is on opponent's current row, it's more likely contested; discourage it slightly.
            row_pen = 2 if ry == oy else 0
            val = (od - sd) - row_pen
            if val > best_val:
                best_val = val
                best_cell = (rx, ry)

    tx, ty = best_cell

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        # Primary: decrease our distance to target.
        our_d = cheb(nx, ny, tx, ty)
        cur_d = cheb(sx, sy, tx, ty)
        prog = cur_d - our_d
        # Secondary: keep away from opponent a bit to reduce late grabs.
        opp_d = cheb(nx, ny, ox, oy)
        score = prog * 10 + opp_d
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]