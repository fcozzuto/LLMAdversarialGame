def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def blocked(nx, ny):
        return (nx, ny) in obs

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cell_score(cx, cy):
        if blocked(cx, cy):
            return -10**9
        best = -10**9
        for rx, ry in resources:
            me_d = abs(rx - cx) + abs(ry - cy)
            opp_d = abs(rx - ox) + abs(ry - oy)
            # Favor resources where we are closer than opponent; slightly prefer nearer targets.
            adv = opp_d - me_d
            tv = adv * 1000 - me_d + (opp_d * 0.001)
            # If opponent is extremely close, penalize less to allow contested grabs.
            if adv < 0:
                tv += adv * 0.2
            if tv > best or (tv == best and (rx, ry) < best_cell):
                best = tv
                best_cell = (rx, ry)
        return best

    best_move = (0, 0)
    best_val = -10**18
    best_cell = (0, 0)

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            val = -10**9
        else:
            # Add a small shaping term to reduce oscillation: prefer moving in direction that decreases distance to best resource.
            # Compute quickly by using the best resource from current position.
            cur_best = resources[0]
            cur_best_tv = None
            for rx, ry in resources:
                me_d0 = abs(rx - x) + abs(ry - y)
                opp_d0 = abs(rx - ox) + abs(ry - oy)
                tv0 = (opp_d0 - me_d0) * 1000 - me_d0 + opp_d0 * 0.001
                if cur_best_tv is None or tv0 > cur_best_tv or (tv0 == cur_best_tv and (rx, ry) < cur_best):
                    cur_best_tv = tv0
                    cur_best = (rx, ry)
            tx, ty = cur_best
            prev_d = abs(tx - x) + abs(ty - y)
            new_d = abs(tx - nx) + abs(ty - ny)
            val = cell_score(nx, ny) + (prev_d - new_d) * 0.5
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]