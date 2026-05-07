def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict) and "x" in a and "y" in a:
            x, y = int(a["x"]), int(a["y"])
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_target(px, py):
        bt = resources[0]
        bd = manh(px, py, bt[0], bt[1])
        for rx, ry in resources[1:]:
            d = manh(px, py, rx, ry)
            if d < bd:
                bd, bt = d, (rx, ry)
        return bt

    my_t = best_target(sx, sy)
    op_t = best_target(ox, oy)

    moves = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        my_d = manh(nx, ny, my_t[0], my_t[1])
        op_d = manh(nx, ny, op_t[0], op_t[1])
        score = my_d * 1000 + op_d  # deterministic: primary reduce own target distance
        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best