def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best_lead = None
    best = None
    for rx, ry in resources:
        me_d = abs(rx - x) + abs(ry - y)
        opp_d = abs(rx - ox) + abs(ry - oy)
        lead = opp_d - me_d
        cand = (lead, -opp_d, -me_d, rx, ry)
        if best_lead is None or cand > best_lead:
            best_lead = cand
            best = (rx, ry, lead, me_d := abs(rx - x) + abs(ry - y), opp_d := abs(rx - ox) + abs(ry - oy))

    target = best[0], best[1]
    if best[2] < 0:
        target = ox, oy

    tx, ty = target
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        opp_dist = abs(ox - nx) + abs(oy - ny)
        score = (-(dist), -opp_dist, -abs(dx) - abs(dy), nx, ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]