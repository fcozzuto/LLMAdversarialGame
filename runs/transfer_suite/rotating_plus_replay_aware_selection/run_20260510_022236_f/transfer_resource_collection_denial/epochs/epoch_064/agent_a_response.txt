def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(x, y, a, b):
        dx = x - a
        if dx < 0: dx = -dx
        dy = y - b
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_ob_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            nx = x + dx
            if nx < 0 or nx >= w:
                continue
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ny = y + dy
                if 0 <= ny < h and (nx, ny) in obs:
                    pen += 1
        return pen

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        val = 0.0
        pen = adj_ob_pen(nx, ny)
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds == 0:
                val += 50.0
            if ds < do:
                val += 20.0 - ds
            elif ds == do:
                val += 6.0 - ds
            else:
                val += 0.5 - 0.2 * ds
        val -= 0.8 * pen
        val += 0.001 * (nx + 2 * ny)  # deterministic tie-break

        if val > best_val:
            best_val = val
            best = (dxm, dym)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]