def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        try:
            x, y = int(x), int(y)
        except Exception:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def step_ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res = observation.get("resources") or []
    best_res = None
    best_d = None
    for r in res:
        if isinstance(r, dict):
            x, y = r.get("x"), r.get("y")
        else:
            x, y = r[0], r[1]
        try:
            x, y = int(x), int(y)
        except Exception:
            continue
        if not inb(x, y) or (x, y) in obstacles:
            continue
        d = manh(sx, sy, x, y)
        if best_d is None or d < best_d or (d == best_d and (x, y) < best_res):
            best_d = d
            best_res = (x, y)

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue
        score = 0
        if best_res is not None:
            score += -manh(nx, ny, best_res[0], best_res[1]) * 3
        d_op = manh(nx, ny, ox, oy)
        score += d_op * 2  # prefer moving away from opponent
        if (nx, ny) == best_res:
            score += 1000
        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]