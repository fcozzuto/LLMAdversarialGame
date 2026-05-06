def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    res_set = set((r[0], r[1]) for r in resources)

    best_target = resources[0]
    best_tv = None
    for r in resources:
        tx, ty = r[0], r[1]
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        tv = (d_opp - d_me) * 1000 - d_me + (0.001 * d_opp)
        if best_tv is None or tv > best_tv or (tv == best_tv and (d_opp < (abs(best_target[0] - x) + abs(best_target[1] - y)))):
            best_target = r
            best_tv = tv

    tx, ty = best_target[0], best_target[1]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        d_me = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        advantage = (d_opp - d_me)
        on_resource = 1 if (nx, ny) in res_set else 0

        # discourage stepping away from target too much, and avoid giving opponent access
        my_to_opp = abs(nx - ox) + abs(ny - oy)
        opp_to_me = abs(ox - nx) + abs(oy - ny)
        proximity_pen = -0.02 * (my_to_opp + opp_to_me)

        # small tie-break: prefer closer to target
        val = advantage * 1000 + on_resource * 50000 - d_me * 3 + proximity_pen
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            if abs(tx - nx) + abs(ty - ny) < abs(tx - (x + best_move[0])) + abs(ty - (y + best_move[1])):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]