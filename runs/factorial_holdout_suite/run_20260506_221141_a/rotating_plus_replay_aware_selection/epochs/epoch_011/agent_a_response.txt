def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    res = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(nx, ny):
        return 0 <= nx < gw and 0 <= ny < gh
    def legal(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    if not res:
        best = None
        bd = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            score = (d, -dx, -dy)
            if best is None or score > best:
                best = score
                bd = (dx, dy)
        return [bd[0], bd[1]]

    best = None
    bd = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_best_adv = None
        my_best_dist = None
        for rx, ry in res:
            my_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            adv = opp_d - my_d  # higher means I reach earlier (or opponent farther)
            if my_best_adv is None or (adv > my_best_adv) or (adv == my_best_adv and my_d < my_best_dist):
                my_best_adv = adv
                my_best_dist = my_d
        # Prefer larger advantage; if equal, prefer shorter my distance; then deterministic tie-break.
        score = (my_best_adv, -my_best_dist, nx - nx // 2, ny - ny // 2, -dx, -dy)
        if best is None or score > best:
            best = score
            bd = (dx, dy)

    return [bd[0], bd[1]]