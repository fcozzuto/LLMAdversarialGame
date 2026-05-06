def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

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

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    if not res:
        return [0, 0]

    def mdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best_cell = res[0]
    best_val = -10**18
    for rx, ry in res:
        sd = mdist(sx, sy, rx, ry)
        od = mdist(ox, oy, rx, ry)
        # Prefer cells where we can arrive sooner; break ties toward closer cells.
        val = (od - sd) * 1000 - sd
        if val > best_val:
            best_val = val
            best_cell = (rx, ry)

    tx, ty = best_cell

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sd = mdist(nx, ny, tx, ty)
        od = mdist(nx, ny, ox, oy)  # implicit: keep pressure/spacing
        # Primary: move closer to target; Secondary: avoid giving opponent too much advantage.
        score = -sd * 10 - mdist(nx, ny, tx, ty) + (mdist(ox, oy, tx, ty) - sd) * 2 + (-(od))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]