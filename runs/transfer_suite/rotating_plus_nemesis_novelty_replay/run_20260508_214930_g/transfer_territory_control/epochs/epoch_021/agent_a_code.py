def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def adj_count(nx, ny, sset):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (nx + dx, ny + dy) in sset:
                    c += 1
        return c

    def dist_to_opponent(nx, ny):
        # min Chebyshev to opponent territory cells (deterministic, no heavy search)
        if not opp_t:
            return 999
        d = 999
        for px, py in opp_t:
            dd = abs(px - nx)
            if dd < d:
                ddy = abs(py - ny)
                cd = dd if dd >= ddy else ddy
                if cd < d:
                    d = cd
        return d

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        target = (nx, ny)

        score = 0
        my_adj = adj_count(nx, ny, self_t)
        op_adj = adj_count(nx, ny, opp_t)

        if target in self_t:
            score += 3 + my_adj * 1.5
        elif target in opp_t:
            # flipping is enabled on entry; strongly prefer grabbing opponent cells near our frontier
            score += 18 + my_adj * 2.0 + op_adj * 0.5
            score -= max(0, dist_to_opponent(nx, ny) - 1) * 0.2
        elif target in unclaimed:
            # claim unclaimed and grow from our adjacency; avoid walking into opponent blobs
            score += 10 + my_adj * 2.0 - op_adj * 1.2
        else:
            # neutral empty (should be rare): still allow movement if it increases adjacency
            score += my_adj * 1.0 - op_adj * 0.6

        # prefer moving toward the closest unclaimed cell if we are not already expanding well
        if unclaimed:
            bestd = 999
            for ux, uy in unclaimed:
                dd = abs(ux - nx)
                dy2 = abs(uy - ny)
                cd = dd if dd >= dy2 else dy2
                if cd < bestd:
                    bestd = cd
                    if bestd == 0:
                        break
            score -= bestd * 0.6

        # slight bias to keep options open (avoid edges only weakly)
        if nx in (0, w - 1) or ny in (0, h - 1):
            score -= 0.3

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]