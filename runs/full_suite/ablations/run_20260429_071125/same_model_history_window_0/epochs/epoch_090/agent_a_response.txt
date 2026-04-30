def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    obst = set((p[0], p[1]) for p in obstacles) if obstacles else set()

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (do - ds, -ds)  # prioritize resources we can reach first
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        hit = 1 if resources and (nx, ny) in set((r[0], r[1]) for r in resources) else 0
        dself = cheb(nx, ny, tx, ty)
        dopp = cheb(ox, oy, tx, ty)
        # prefer hitting, then reducing distance to target; small tie-break to not give target to opponent
        score = hit * 1_000_000 + (dopp - dself) * 10_000 - dself
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move