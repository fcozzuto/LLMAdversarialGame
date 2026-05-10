def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    res = observation.get("resources") or []
    resources = [tuple(p) for p in res if isinstance(p, (list, tuple)) and len(p) >= 2]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if resources:
        tx, ty = min(resources, key=lambda p: manh(sx, sy, p[0], p[1]))[:2]
    else:
        tx, ty = ox, oy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                valid.append((dx, dy, nx, ny))

    best = None
    for dx, dy, nx, ny in valid:
        dtar = manh(nx, ny, tx, ty)
        dop = manh(nx, ny, ox, oy)
        cand = (dtar, -dop, dx, dy)
        if best is None or cand < best[0]:
            best = (cand, [dx, dy])
    return best[1]