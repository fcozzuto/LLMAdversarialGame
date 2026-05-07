def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    res = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not res:
        # stay away from walls/obstacles deterministically
        best = None
        for dx, dy, nx, ny in legal:
            score = (min(nx, w - 1 - nx) + min(ny, h - 1 - ny)) * 2
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]]

    best = None
    for dx, dy, nx, ny in legal:
        s_best = 10**9
        o_best = 10**9
        for r in res:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                s_d = man(nx, ny, rx, ry)
                o_d = man(ox, oy, rx, ry)
                if s_d < s_best:
                    s_best = s_d
                if o_d < o_best:
                    o_best = o_d
        # Prefer arriving earlier to some resource; tie-break by closer resource.
        score = (o_best - s_best) * 1000 - s_best
        if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
            best = (score, (dx, dy))
    return [best[1][0], best[1][1]]