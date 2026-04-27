def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    resources = []
    for p in observation.get("resources", []):
        if len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    neigh = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def step_scores(tx, ty):
        bx = 10**9
        best = (0, 0)
        for dx, dy in neigh:
            nx, ny = clamp(sx + dx, sy + dy)
            if (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            ed = abs(nx - ox) + abs(ny - oy)
            score = -d + 0.05 * ed
            if score > bx:
                bx = score
                best = (dx, dy)
        return best

    if resources:
        target = min(resources, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
        return list(step_scores(target[0], target[1]))

    cx, cy = w // 2, h // 2
    dx, dy = step_scores(cx, cy)
    return [int(dx), int(dy)]