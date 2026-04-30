def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_pen(x, y):
        if not inb(x, y): return 10**8
        if (x, y) in obstacles: return 10**7
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    p += 6
        return p

    def beat_resource_value(nx, ny, rx, ry):
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can beat (closer than opponent); also avoid very slow paths.
        return (do - ds) * 10 - ds

    best_move = (0, 0)
    best_val = -10**30

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            v = -cheb(nx, ny, tx, ty) - obst_pen(nx, ny)
            if v > best_val or (v == best_val and (dx, dy) < best_move):
                best_val, best_move = v, (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        p = obst_pen(nx, ny)
        if p >= 10**7:
            continue
        # Greedy over resources: maximize best "beat" advantage.
        best_res = -10**30
        for rx, ry in resources:
            v = beat_resource_value(nx, ny, rx, ry)
            if v > best_res:
                best_res = v
        # Small step preference to keep momentum.
        stepish = -cheb(nx, ny, sx, sy)
        vtot = best_res + stepish - p
        if vtot > best_val or (vtot == best_val and (dx, dy) < best_move):
            best_val, best_move = vtot, (dx, dy)

    return [best_move[0], best_move[1]]