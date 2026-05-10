def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_count(nx, ny, sset):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (nx + dx, ny + dy) in sset:
                        c += 1
        return c

    ox, oy = observation["opponent_position"]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        target = (nx, ny)
        ds = abs(nx - ox) + abs(ny - oy)  # smaller => closer to opponent
        a_self = adj_count(nx, ny, self_t)
        a_opp = adj_count(nx, ny, opp_t)

        score = 0
        if target in self_t:
            score += 3 + 0.5 * a_self - 0.25 * a_opp
        elif target in opp_t:
            score += 12 + 2.0 * a_self + 0.25 * a_opp  # flip is valuable
        else:
            score += 2 + 2.5 * a_self + 1.0 * a_opp  # expand while enabling flips
            # slightly prefer moves that keep distance from opponent when on neutral territory
            score += 0.06 * ds

        # edge/center shaping: lightly push toward center for faster territory accumulation
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score += 0.03 * (-(abs(nx - cx) + abs(ny - cy)))

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move