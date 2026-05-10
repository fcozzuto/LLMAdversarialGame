def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    base_dist_to_opp = abs(sx - ox) + abs(sy - oy)

    targets = list(unclaimed)
    if targets:
        best_target = None
        best_val = -10**18
        for tx, ty in targets:
            d_us = abs(tx - sx) + abs(ty - sy)
            d_opp = abs(tx - ox) + abs(ty - oy)
            d_center = abs(tx - cx) + abs(ty - cy)
            # Prefer close to us, far from opponent, and not too central (counter-center-claim)
            val = (d_opp - d_us) * 6 + (18 - d_center) * 1.5
            # Small nudge toward unexplored/edge areas
            val += (tx + (w - 1 - tx) + ty + (h - 1 - ty)) * 0.02
            if val > best_val:
                best_val = val
                best_target = (tx, ty)
    else:
        best_target = (ox, oy)

    tx, ty = best_target
    # Evaluate each move by its effect toward target and by territory flipping
    best_move = (0, 0)
    best_score = -10**18
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue
        score = 0.0
        if (nx, ny) in opp_t:
            score += 2500
        elif (nx, ny) in unclaimed:
            score += 60
        elif (nx, ny) in self_t:
            score += 8

        d_to_target = abs(nx - tx) + abs(ny - ty)
        d_to_opp = abs(nx - ox) + abs(ny - oy)

        score += (20 - d_to_target) * 3.0
        score += (d_to_opp - base_dist_to_opp) * -2.0  # prefer moving away from opponent
        # Additional anti-center pressure
        score += (abs(sx - cx) + abs(sy - cy) - (abs(nx - cx) + abs(ny - cy))) * 6.0

        # Avoid getting stuck: slight penalty for staying still unless forced
        if ddx == 0 and ddy == 0:
            score -= 2.0

        # If move reduces distance to opponent territory-front, reward more
        if opp_t:
            nearest_opp_front = None
            nearest_d = 10**9
            for px, py in opp_t:
                d = abs(nx - px) + abs(ny - py)
                if d < nearest_d:
                    nearest_d = d
                    nearest_opp_front = (px, py)
            score += max(0, 8 - nearest_d) * 4.0

        if score > best_score:
            best_score = score
            best_move = (ddx, ddy)

    dx, dy = best_move
    return [int(dx), int(dy)]