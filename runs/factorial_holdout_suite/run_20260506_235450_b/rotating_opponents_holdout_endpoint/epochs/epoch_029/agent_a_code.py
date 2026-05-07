def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, dict):
            if "x" in a and "y" in a:
                x, y = int(a["x"]), int(a["y"])
                if 0 <= x < w and 0 <= y < h:
                    obstacles.add((x, y))
        elif isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, dict):
            if "x" in r and "y" in r:
                x, y = int(r["x"]), int(r["y"])
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if resources:
        def dist(x1, y1, x2, y2):
            dx = x1 - x2
            if dx < 0: dx = -dx
            dy = y1 - y2
            if dy < 0: dy = -dy
            return dx + dy
        tx, ty = min(resources, key=lambda p: (dist(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        op = observation.get("opponent_position") or [w - 1, h - 1]
        tx, ty = int(op[0]), int(op[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = abs(nx - tx) + abs(ny - ty)
        if best is None or sc < best_score or (sc == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = sc

    if best is not None:
        return [best[0], best[1]]

    if valid(sx, sy):
        return [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]