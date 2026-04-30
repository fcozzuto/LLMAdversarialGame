def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    tx, ty = None, None
    if resources:
        best = None
        for rx, ry in resources:
            d = md(sx, sy, rx, ry)
            if best is None or d < best[0] or (d == best[0] and (rx, ry) < best[1]):
                best = (d, (rx, ry))
        tx, ty = best[1]

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            if tx is not None:
                score = md(nx, ny, tx, ty)
                cand.append((score, abs(dx) + abs(dy), (dx, dy), md(nx, ny, ox, oy)))
            else:
                cand.append((md(nx, ny, ox, oy), abs(dx) + abs(dy), (dx, dy), 0))

    if cand:
        if tx is not None:
            cand.sort(key=lambda t: (t[0], t[3], t[1], t[2][0], t[2][1]))
            return [int(cand[0][2][0]), int(cand[0][2][1])]
        else:
            cand.sort(key=lambda t: (-t[0], t[1], t[2][0], t[2][1]))
            return [int(cand[0][2][0]), int(cand[0][2][1])]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [int(dx), int(dy)]
    return [0, 0]