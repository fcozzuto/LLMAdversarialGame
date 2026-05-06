def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
    def center_bias(x, y):
        dx = x - cx0; dy = y - cy0
        return -(dx * dx + dy * dy) * 0.01

    best = [0, 0]; best_val = -10**18
    has_res = bool(resources)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue

        val = center_bias(nx, ny)  # base stability

        if has_res:
            # Prefer moves that create a winning distance gap to some resource,
            # and also discourage giving the opponent an easy grab.
            best_local = -10**18
            for rx, ry in resources:
                dme = man(nx, ny, rx, ry)
                dop = man(ox, oy, rx, ry)
                gap = dop - dme  # positive means we are closer than opponent
                # Strongly prioritize resources that we can reach sooner,
                # but still allow slight progress if opponent is also far.
                score = gap * 3.5 - dme * 0.12
                # If we're already adjacent to the resource, boost more.
                if dme == 0:
                    score += 50
                elif dme == 1:
                    score += 10
                # Penalize moves that would let opponent be adjacent while we aren't.
                if dop == 1 and dme > 1:
                    score -= 8
                if score > best_local:
                    best_local = score

            val += best_local

            # Interception bias: if opponent is moving toward a resource,
            # steer toward the same region when we can't immediately out-gap.
            # Approximate opponent pressure by considering nearest resource to opponent.
            opp_best = 10**9; opp_rx, opp_ry = None, None
            for rx, ry in resources:
                d = man(ox, oy, rx, ry)
                if d < opp_best:
                    opp_best = d; opp_rx, opp_ry = rx, ry
            if opp_rx is not None:
                dist_to_opp_target = man(nx, ny, opp_rx, opp_ry)
                val += (-dist_to_opp_target) * 0.12
        else:
            # No visible resources: move to the closest board edge to reposition for future grabs.
            edge_dist = min(nx, w - 1 - nx, ny, h - 1 - ny)
            val += -edge_dist * 0.05

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return [int(best[0]), int(best[1])]