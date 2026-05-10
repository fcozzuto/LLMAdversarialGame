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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neigh8(x, y):
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                yield nx, ny

    # Prefer expanding around our current territory, but also allow strategic "harassment" into opponent cells.
    best_move = (0, 0)
    best_score = -10**18
    base_to_opp = abs(sx - ox) + abs(sy - oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        score = 0
        if (nx, ny) in opp_t:
            score += 1200  # strong: entering flips control (if enabled)
        if (nx, ny) in unclaimed:
            score += 120
        if (nx, ny) in self_t:
            score += 25

        # Expansion: move toward cells that border our territory (deterministic frontier following).
        border_self = 0
        for ax, ay in neigh8(nx, ny):
            if (ax, ay) in self_t:
                border_self += 1
        score += border_self * 18

        # Avoid walking into opponent territory too carelessly (keep pressure but don't suicide-divert).
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        score += (base_to_opp - dist_to_opp) * 3  # closer to opponent generally good

        # If we're already close to opponent, prioritize capturing; otherwise, expand territory.
        if base_to_opp <= 6:
            score += (1 if (nx, ny) in opp_t else 0) * 400
            score -= dist_to_opp * 2
        else:
            score += (1 if (nx, ny) in unclaimed else 0) * 40
            score -= dist_to_opp * 1

        # Mild preference to reduce distance to the "front" toward unclaimed near our territory.
        # Use local proxy: count neighboring unclaimed.
        border_unclaimed = 0
        for ax, ay in neigh8(nx, ny):
            if (ax, ay) in unclaimed:
                border_unclaimed += 1
        score += border_unclaimed * 8

        # Tie-break deterministically: prefer moves that reduce manhattan to opponent, then lexicographic dx,dy.
        cand = (score, -(abs(nx - ox) + abs(ny - oy)), dx, dy)
        best_cand = (best_score, -(abs(best_move[0] + sx - ox) + abs(best_move[1] + sy - oy)), best_move[0], best_move[1])
        if cand > best_cand:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]