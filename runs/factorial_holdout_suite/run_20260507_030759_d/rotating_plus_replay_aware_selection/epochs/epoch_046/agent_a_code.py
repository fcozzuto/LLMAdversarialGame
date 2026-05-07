def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        obstacles.add((p[0], p[1]))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    res_sorted = sorted((r[0], r[1]) for r in resources)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 10**18, 10**18)
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        local = (-10**18, 10**18, 10**18, None)
        for rx, ry in res_sorted:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # higher is better (we are closer)
            cand = (adv, sd, od, (rx, ry))
            if cand[0] > local[0] or (cand[0] == local[0] and (cand[1] < local[1] or (cand[1] == local[1] and cand[2] < local[2]))):
                local = cand
        if local[3] is None:
            continue
        if local[0] > best[0] or (local[0] == best[0] and (local[1] < best[1] or (local[1] == best[1] and local[2] < best[2]))):
            best = local[:3]
            best_move = [dx, dy]
    return best_move