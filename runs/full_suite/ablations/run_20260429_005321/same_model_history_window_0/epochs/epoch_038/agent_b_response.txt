def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] or []
    obstacles = set(tuple(p) for p in (observation["obstacles"] or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    if resources:
        best_t = None
        best_adv = -10**18
        for i, (rx, ry) in enumerate(resources):
            myd = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
            opd = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
            adv = (opd - myd) * 1000 - myd + (0.001 * (len(resources) - i))
            if adv > best_adv:
                best_adv = adv
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = (ox, oy)

    def move_ok(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obstacles

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not move_ok(nx, ny):
            continue
        if nx == ox and ny == oy:
            continue
        dist_after = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        dist_before = (tx - sx) * (tx - sx) + (ty - sy) * (ty - sy)
        opp_after = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        score = (dist_before - dist_after) * 10 + opp_after * 0.001 - dist_after * 0.0001
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]