def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def score(nx, ny, tx, ty):
        d = abs(tx - nx) + abs(ty - ny)
        adv = -d
        od = abs(ox - nx) + abs(oy - ny)
        block = 0
        return adv + 0.05 * od + block

    if resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = min(score(nx, ny, rx, ry) for rx, ry in resources)
            if best is None or v > best[0]:
                best = (v, dx, dy)
        return [0, 0] if best is None else [int(best[1]), int(best[2])]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = abs(ox - nx) + abs(oy - ny)
        if best is None or v > best[0]:
            best = (v, dx, dy)
    return [0, 0] if best is None else [int(best[1]), int(best[2])]