def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        tx, ty = (w - 1 - ox, h - 1 - oy)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        for ddx, ddy in [(0, 0), (dx, 0), (0, dy), (dx, ddy)]:
            nx, ny = sx + ddx, sy + ddy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [ddx, ddy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**9

    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # Choose the best resource to move toward for this single step.
        local_best = -10**9
        for tx, ty in resources:
            self_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            v = (10**6 if self_d == 0 else 0) + (opp_d - self_d) * 1000 - self_d
            if v > local_best:
                local_best = v
        if local_best > bestv or (local_best == bestv and (ddx, ddy) < best):
            bestv = local_best
            best = (ddx, ddy)

    return [best[0], best[1]] if best is not None else [0, 0]