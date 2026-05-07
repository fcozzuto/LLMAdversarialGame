def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    ti = int(observation.get("turn_index", 0) or 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_step(tx, ty):
        candidates = []
        for dx, dy in moves:
            nx = sx + dx
            ny = sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                score = md(nx, ny, tx, ty) + 0.01 * ((sx + sy + ti) % 7)
                candidates.append((score, dx, dy))
        if not candidates:
            return (0, 0)
        candidates.sort(key=lambda z: (z[0], z[1], z[2]))
        return (candidates[0][1], candidates[0][2])

    if resources:
        best = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            val = (opd - myd) * 1000 - myd
            tie = (rx * 31 + ry * 17 + ti) % 997
            if best is None or (val, tie) > best[0]:
                best = ((val, tie), rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w - 1, h - 1) if ((ti % 2) == 0) else (0, 0)
        if (tx, ty) in obstacles:
            tx, ty = (0, h - 1) if (0, h - 1) not in obstacles else (w - 1, 0)

    dx, dy = best_step(tx, ty)
    return [int(dx), int(dy)]