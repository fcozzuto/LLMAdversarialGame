def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_t = resources[0]
    best_v = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        v = (od - sd) * 100 - sd
        # slight bias toward nearer resources if we can still be competitive
        if sd <= 2:
            v += 5
        if v > best_v:
            best_v = v
            best_t = (rx, ry)

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_s = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # prefer improving win-likelihood plus moving closer to target
        s = (od - sd) * 100 - sd * 2
        # anti-jam: if we're not making progress toward target, penalize
        if sd >= cheb(sx, sy, tx, ty):
            s -= 3
        if s > best_s:
            best_s = s
            best_move = [dx, dy]

    return best_move