def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx = 1 if sx > gw // 2 else gw - 2
        ty = 1 if sy > gh // 2 else gh - 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -md(nx, ny, tx, ty)
            if v > bestv or (v == bestv and (nx, ny) != (sx, sy)):
                bestv = v
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_score = -10**18
    best_tiebreak = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # If landing on a resource, prioritize strongly.
        landed = 1 if (nx, ny) in obstacles else 0
        self_to_res = 10**18
        opp_to_res = 10**18
        for rx, ry in resources:
            d1 = md(nx, ny, rx, ry)
            if d1 < self_to_res: self_to_res = d1
            d2 = md(ox, oy, rx, ry)
            if d2 < opp_to_res: opp_to_res = d2

        # Score favors states where we are closer than opponent to at least one resource.
        # Also slightly penalizes being far from the closest resource after the move.
        closest_res_after = self_to_res
        opp_min = opp_to_res
        score = (opp_min - closest_res_after) * 10 - closest_res_after
        # Extra deterministic push to avoid mirroring opponent paths too much: prefer decreasing x when tied
        if score > best_score or (score == best_score and (closest_res_after < best_tiebreak or (closest_res_after == best_tiebreak and (nx, ny) < (sx + best_move[0], sy + best_move[1])))):
            best_score = score
            best_tiebreak = closest_res_after
            best_move = [dx, dy]

    return best_move