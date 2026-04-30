def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        for ddx, ddy in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            nx, ny = sx + ddx, sy + ddy
            if ok(nx, ny):
                return [ddx, ddy]
        for ddx, ddy in dirs:
            nx, ny = sx + ddx, sy + ddy
            if ok(nx, ny):
                return [ddx, ddy]
        return [0, 0]

    if resources:
        best = None
        bestd = 10**9
        for x, y in resources:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd:
                bestd = d
                best = (x, y)
        return step_toward(best[0], best[1])

    tx = w - 1 if sx < w // 2 else 0
    ty = h - 1 if sy < h // 2 else 0
    return step_toward(tx, ty)