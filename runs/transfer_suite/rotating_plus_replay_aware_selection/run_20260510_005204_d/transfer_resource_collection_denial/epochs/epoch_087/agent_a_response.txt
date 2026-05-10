def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    res = [tuple(r) for r in resources]
    res_set = set(res)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    late = 1 if turns_remaining <= 10 else 0
    w_capture = 10**6
    w_adv = 1000
    w_opp = 10 if late else 50  # be more aggressive late

    best_score = -10**30
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy

        if (nx, ny) in res_set:
            score = w_capture
            if late:
                my_min = 0
                opp_min = min(cheb(ox, oy, rx, ry) for rx, ry in res)
                score += w_adv * (opp_min - my_min)
            if score > best_score:
                best_score, best_move = score, (nx - sx, ny - sy)
            continue

        my_min = 10**9
        opp_min = 10**9
        for rx, ry in res:
            d1 = cheb(nx, ny, rx, ry)
            if d1 < my_min: my_min = d1
            d2 = cheb(ox, oy, rx, ry)
            if d2 < opp_min: opp_min = d2

        adv = opp_min - my_min  # positive means we are closer than opponent
        score = w_adv * adv - w_opp * my_min
        if score > best_score:
            best_score, best_move = score, (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]