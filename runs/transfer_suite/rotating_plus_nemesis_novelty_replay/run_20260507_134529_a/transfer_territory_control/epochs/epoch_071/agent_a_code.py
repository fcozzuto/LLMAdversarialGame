def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    resources = to_set("resources")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        tx, ty = min(resources, key=lambda p: (manh(sx, sy, p[0], p[1]), p[0], p[1]))
        best = (-10**9, None)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not cell_ok(nx, ny):
                continue
            score = -manh(nx, ny, tx, ty) + 0.1 * manh(nx, ny, ox, oy)
            if score > best[0]:
                best = (score, (dx, dy))
        if best[1] is not None:
            return [best[1][0], best[1][1]]

    best = (-10**9, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        score = -manh(nx, ny, ox, oy)
        if score > best[0]:
            best = (score, (dx, dy))
    return [best[1][0], best[1][1]]