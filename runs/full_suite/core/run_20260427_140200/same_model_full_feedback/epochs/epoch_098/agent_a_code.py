def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def step_toward(tx, ty):
        dx = tx - sx
        dy = ty - sy
        mx = 0 if dx == 0 else (1 if dx > 0 else -1)
        my = 0 if dy == 0 else (1 if dy > 0 else -1)
        nx, ny = sx + mx, sy
        if mx != 0 and 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [mx, 0]
        nx, ny = sx, sy + my
        if my != 0 and 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [0, my]
        for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)):
            nx, ny = sx + a, sy + b
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [a, b]
        return [0, 0]

    target = None
    best = None
    if resources:
        for x, y in resources:
            d = abs(x - sx) + abs(y - sy)
            if best is None or d < best or (d == best and (x, y) < target):
                best = d
                target = (x, y)
        return step_toward(target[0], target[1])

    cx, cy = w // 2, h // 2
    if (sx, sy) == (cx, cy):
        cx, cy = ox, oy
    return step_toward(cx, cy)