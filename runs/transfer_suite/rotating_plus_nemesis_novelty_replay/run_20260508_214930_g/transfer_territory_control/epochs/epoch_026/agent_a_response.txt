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

    def in_bounds_count(nx, ny, sset):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in sset:
                    c += 1
        return c

    # Potential-field style: advance into unclaimed, expand frontier, and avoid opponent-adjacent duel zones.
    best_move = (0, 0)
    best_score = -10**18
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        is_own = (nx, ny) in self_t
        is_opp = (nx, ny) in opp_t
        is_un = (nx, ny) in unclaimed

        opp_adj = in_bounds_count(nx, ny, opp_t)
        un_adj = in_bounds_count(nx, ny, unclaimed)

        # Prefer claiming; if forced to step into opponent territory, do it only when it reduces risk.
        center_bias = -abs(nx - cx) - abs(ny - cy)  # slight pull toward center to contest center-claimer
        dist_from_opp = 0
        if opp_t:
            # approximate distance via local neighborhood: reward being farther from opponent territory
            # (use inverse of local opponent adjacency mostly; deterministic and cheap)
            dist_from_opp = (8 - opp_adj)

        score = 0
        score += 8 if is_un else 0
        score += 3 if (nx, ny) in self_t else 0
        score += 2 * un_adj
        score += 0.15 * center_bias
        score += 1.5 * dist_from_opp
        score -= 4.5 * opp_adj
        score -= 8.0 if is_opp and opp_adj > 0 else (0.0 if is_opp else 0.0)

        # Ensure we don't just oscillate: small penalty for returning to a previous self cell (if observation has path, it's always False here).
        if (nx, ny) in self_t and is_un is False and opp_adj >= 2:
            score -= 1.0

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]