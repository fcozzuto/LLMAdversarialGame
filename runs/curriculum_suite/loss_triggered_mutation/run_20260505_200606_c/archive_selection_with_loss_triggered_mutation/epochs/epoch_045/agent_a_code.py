def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**9

    def safe_cell(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe_cell(nx, ny):
            continue
        if resources:
            sd = 10**9
            od = 10**9
            for rx, ry in resources:
                d1 = md(nx, ny, rx, ry)
                if d1 < sd: sd = d1
                d2 = md(ox, oy, rx, ry)
                if d2 < od: od = d2
            val = (od - sd) * 100 - sd
            if (nx, ny) in resources:
                val += 10**6
        else:
            sd = md(nx, ny, ox, oy)
            val = sd * 10 + (0 if (nx, ny) not in obs else -10**6)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    if safe_cell(sx, sy):
        return [int(best_move[0]), int(best_move[1])]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if safe_cell(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]