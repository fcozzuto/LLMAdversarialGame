def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def eval_pos(px, py):
        best = -10**9
        best2 = -10**9
        for tx, ty in resources:
            ds = cheb(px, py, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Prefer resources that we can secure earlier than opponent; otherwise deny by increasing opponent disadvantage.
            adv = (do - ds) * 100 - ds
            # Small deterministic tie-break to prefer higher x then lower y.
            adv += (tx * 2 - ty)
            if adv > best:
                best2 = best
                best = adv
            elif adv > best2:
                best2 = adv
        return best

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic preference order: closer to opponent's corner helps intercept.
    candidates.sort(key=lambda d: (d[0] == 0 and d[1] == 0, -(sx + d[0] + (sy + d[1]) * 0.01), d[0], d[1]))

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        val = eval_pos(nx, ny)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    if best_move == [0, 0]:
        # If blocked all candidates (unlikely), stay.
        return [0, 0]
    return best_move