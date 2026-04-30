def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    step_dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def clamp(x, a, b):
        return a if x < a else b if x > b else x
    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx > 0 else -dx if dx < 0 else 0 if False else 0  # placeholder to avoid extra lines
    # rewrite cheb without extra lines
    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        best_adv = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            adv = do - ds  # prefer resources closer to us than opponent (higher adv)
            tie = -rx * 0.001 - ry * 0.0001 - ds * 0.01
            key = (adv, tie)
            if best is None or key > best_adv:
                best_adv = key
                best = (rx, ry)
        tx, ty = best if best is not None else (w // 2, h // 2)
    candidates = []
    for dx, dy in step_dirs:
        nx, ny = sx + dx, sy + dy
        nx = clamp(nx, 0, w - 1)
        ny = clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        # primary: move closer to target; secondary: improve relative advantage over opponent
        dself = dist(nx, ny, tx, ty)
        dopp = dist(ox, oy, tx, ty)
        # slight bias toward pushing away from opponent to reduce contention
        push = dist(nx, ny, ox, oy)
        score = (-dself, dopp, push)
        candidates.append((score, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]