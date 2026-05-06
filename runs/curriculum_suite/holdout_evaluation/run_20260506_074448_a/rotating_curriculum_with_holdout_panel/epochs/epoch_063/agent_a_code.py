def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    deltas = [(-1, -1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    # Deterministic "deny-aware" heuristic:
    # Prefer moves that increase how many resources we can reach strictly earlier than opponent,
    # and secondarily moves that reduce opponent's advantage; avoid obstacles heavily.
    best = [0, 0]; best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue

        if not resources:
            # fallback: mirror a simple pursuit of center to stay useful
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            val = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
            if val > best_val:
                best_val = val; best = [dx, dy]
            continue

        my_adv_count = 0
        opp_adv_count = 0
        my_close = 10**9
        opp_close = 10**9

        # compute counts; small tie-breaking by nearest resource and by lowering opponent access
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_my = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            if d_my < d_opp:
                my_adv_count += 1
            elif d_opp < d_my:
                opp_adv_count += 1
            if d_my < my_close: my_close = d_my
            if d_opp < opp_close: opp_close = d_opp

        # "swing" term: emphasize reducing opponent advantage; keep some pressure on our proximity
        val = 5.0 * my_adv_count - 4.0 * opp_adv_count
        # If we can win any resource race, push toward the closest one; otherwise deny by reducing opp reach
        if my_adv_count > 0:
            val += 0.4 / (1 + my_close)
        else:
            val += 0.25 / (1 + opp_close)

        # slight preference to keep distance from opponent for denying interference (resource_denier dislikes chase)
        val += 0.01 * (man(nx, ny, ox, oy))

        if val > best_val:
            best_val = val; best = [dx, dy]

    return [int(best[0]), int(best[1])]