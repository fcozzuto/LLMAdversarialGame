def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def clamp(nx, ny):
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return nx, ny
        return sx, sy

    def step_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = clamp(sx + dx, sy + dy)
        return nx - sx, ny - sy

    if resources:
        best = None
        for r in resources:
            sd = man((sx, sy), r)
            od = man((ox, oy), r)
            score = (od - sd) * 10 - sd  # prioritize resources we can reach first
            cand = (score, -sd, r[0], r[1])
            if best is None or cand > best:
                best = cand
        tx, ty = best[2], best[3]
        dx, dy = step_towards(tx, ty)
        if (dx, dy) == (0, 0) and (sx, sy) != (tx, ty):
            dx = 1 if tx > sx else -1 if tx < sx else 0
            dy = 1 if ty > sy else -1 if ty < sy else 0
            nx, ny = clamp(sx + dx, sy + dy)
            return [nx - sx, ny - sy]
        return [dx, dy]

    # No visible resources: drift toward center while avoiding obstacles
    target = (w // 2, h // 2)
    cx, cy = target
    dx = 0 if cx == sx else (1 if cx > sx else -1)
    dy = 0 if cy == sy else (1 if cy > sy else -1)
    nx, ny = clamp(sx + dx, sy + dy)
    return [nx - sx, ny - sy]