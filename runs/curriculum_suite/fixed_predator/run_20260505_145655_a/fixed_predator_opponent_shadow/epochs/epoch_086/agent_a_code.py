def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best_r = None
    best_tv = None
    for tx, ty in resources:
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        tv = (d_opp - d_me) * 1000 - d_me + (0.001 * d_opp)
        if best_tv is None or tv > best_tv or (tv == best_tv and (d_opp < (abs(best_r[0] - x) + abs(best_r[1] - y)))):
            best_tv = tv
            best_r = [tx, ty]

    # Local interception/greedy step with simple obstacle penalty
    target = best_r
    tx, ty = target[0], target[1]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = [0, 0]
    best_s = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            nx, ny = x, y  # engine keeps in place on invalid/blocked moves
        d_me2 = abs(tx - nx) + abs(ty - ny)
        d_opp2 = abs(tx - ox) + abs(ty - oy)
        # If we move closer than before, reward; if closer for opponent, penalize slightly
        prev_me = abs(tx - x) + abs(ty - y)
        closer = prev_me - d_me2
        hit = 1 if (nx, ny) == (tx, ty) else 0
        # Also consider pulling away from nearest resource to opponent when we can't reach quickly
        opp_closest = None
        for rx, ry in resources:
            d = abs(rx - ox) + abs(ry - oy)
            if opp_closest is None or d < opp_closest:
                opp_closest = d
        s = (hit * 50000) + (closer * 2000) + (-(d_me2) * 10) + (-(d_opp2) * 2)
        if best_s is None or s > best_s or (s == best_s and (dx, dy) < (best_m[0], best_m[1])):
            best_s = s
            best_m = [dx, dy]

    # Secondary bias: if opponent is much closer to the same best target, try to cut diagonally toward it
    d_me = abs(tx - x) + abs(ty - y)
    d_opp = abs(tx - ox) + abs(ty - oy)
    if d_opp + 2 < d_me:
        dx = sign(tx - x)
        dy = sign(ty - y)
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny) and not blocked(nx, ny):
            return [dx, dy]

    return best_m