def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        return [0, 0]

    res = [tuple(r) for r in resources]
    res_set = set(res)

    def min_dist_to_resources(x, y):
        best = 10**9
        for rx, ry in res:
            d = abs(rx - x) + abs(ry - y)
            if d < best:
                best = d
        return best

    opp_min = min_dist_to_resources(ox, oy)
    my_min = min_dist_to_resources(sx, sy)

    # Select nearest resource deterministically for direction bias.
    # Tie-break by (dist, rx, ry).
    best_r = None
    best_key = (10**9, 10**9, 10**9)
    for rx, ry in res:
        d = abs(rx - sx) + abs(ry - sy)
        key = (d, rx, ry)
        if key < best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) in res_set:
            pickup = 30
        else:
            pickup = 0

        d_to = abs(tx - nx) + abs(ty - ny)
        my_d = min_dist_to_resources(nx, ny)

        # Favor reducing our distance and beating opponent's nearest resource race.
        beat = opp_min - my_d

        # Small tie-breaker to keep moving generally toward the chosen nearest target.
        toward = -(abs(tx - nx) + abs(ty - ny))

        # Also discourage stepping away when we already are close.
        closeness = 0 if my_min >= 10 else (10 - my_d)

        val = pickup + 2.2 * beat + 0.8 * toward + 0.3 * closeness - 0.05 * d_to
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move