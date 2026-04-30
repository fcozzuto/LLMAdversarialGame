def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    x0, y0 = int(self_pos[0]), int(self_pos[1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])
    obs_set = {(int(a), int(b)) for a, b in obstacles}
    res_set = {(int(a), int(b)) for a, b in resources}

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = (-10**18, 0, 0)
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))
    # deterministic tie-break: prefer smaller |dx| then smaller |dy| then order
    moves.sort(key=lambda t: (abs(t[0]), abs(t[1]), t[0], t[1]))

    for dx, dy in moves:
        x, y = x0 + dx, y0 + dy
        if not inside(x, y):
            continue
        if (x, y) in obs_set:
            continue

        if (x, y) in res_set:
            score = 10**9 + 10**6 * (1 if resources else 0)  # immediate pick
        else:
            best_adv = -10**9
            best_opp_dist = 10**9
            for rx, ry in resources:
                sx_d = man(x, y, rx, ry)
                o_d = man(ox, oy, rx, ry)
                adv = o_d - sx_d  # positive means we are closer
                if adv > best_adv:
                    best_adv = adv
                    best_opp_dist = o_d
                elif adv == best_adv and o_d < best_opp_dist:
                    best_opp_dist = o_d
            # encourage moving toward any resource, and slightly away from opponent
            d_to_opp = max(0, man(x, y, ox, oy))
            score = 50 * best_adv - man(x, y, x0, y0) + 0.5 * d_to_opp

        # tie-break deterministically
        score -= 0.01 * (dx * dx + dy * dy)
        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]