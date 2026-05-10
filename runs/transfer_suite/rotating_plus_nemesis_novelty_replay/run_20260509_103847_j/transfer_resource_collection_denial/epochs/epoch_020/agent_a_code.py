def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_target():
        best = None
        best_key = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer: we are no worse (sd<=od), then smaller sd, then slightly punish if opponent is much closer
            if sd <= od:
                key = (0, sd, od - sd, rx, ry)
            else:
                key = (1, od, sd - od, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = best_target()

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            continue
        sd_before = man(sx, sy, tx, ty)
        od_before = man(ox, oy, tx, ty)
        sd_after = man(nx, ny, tx, ty)
        od_after = od_before  # opponent position static this turn
        # Primary: improve lead at target; Secondary: get closer; Tertiary: avoid overshooting other favorable resources
        lead_delta = (sd_before - od_before) - (sd_after - od_after)
        dist = sd_after
        # Consider whether stepping onto/near a resource we currently contest improves overall
        near_bonus = 0
        for rx, ry in resources:
            if (rx, ry) == (nx, ny):
                near_bonus = 1000
                break
            d = man(nx, ny, rx, ry)
            if d <= 2 and man(sx, sy, rx, ry) <= man(ox, oy, rx, ry):
                near_bonus = max(near_bonus, 3 - d)
        val = (-(lead_delta), dist, -near_bonus, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]