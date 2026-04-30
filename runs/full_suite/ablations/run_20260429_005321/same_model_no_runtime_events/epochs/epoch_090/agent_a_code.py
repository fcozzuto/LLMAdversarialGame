def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not valid(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        tx, ty = min(resources, key=lambda r: (man(sx, sy, r[0], r[1]), r[1], r[0]))
        best = None
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dres = man(nx, ny, tx, ty)
            dop = man(nx, ny, ox, oy)
            score = (-dres * 10) + (dop)  # deterministic: fixed tie via delta order
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dop = man(nx, ny, ox, oy)
            dcent = man(nx, ny, cx, cy)
            score = (dop * 10) - dcent
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]