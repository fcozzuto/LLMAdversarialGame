def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w - 1, h - 1
        if ox > sx:
            tx = 0
        if oy > sy:
            ty = 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [int(dx), int(dy)]

    # Prefer moves that (1) create a lead on some resource, (2) reduce our distance to that resource,
    # and (3) worsen opponent access to resources we might contest.
    best = None
    best_val = -10**18
    best_tiebreak = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        max_term = -10**18
        min_self_d = 10**18

        for rx, ry in resources:
            rx = int(rx)
            ry = int(ry)
            self_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)

            # Lead to be first; opponent_denier tends to block, so punish situations where we are behind.
            lead = opp_d - self_d  # positive means we are closer than opponent
            # Strongly favor getting any lead quickly; add distance-based shaping.
            term = (lead * 1000) - self_d * 3

            # If we are still behind, still consider it, but much less; also penalize allowing opponent closeness.
            if lead < 0:
                term = term - (-lead) * 6 - opp_d

            if term > max_term:
                max_term = term
            if self_d < min_self_d:
                min_self_d = self_d

        # Small deterministic tiebreak: prefer smaller min_self_d then lexicographic move order.
        val = max_term
        if val > best_val or (val == best_val and min_self_d < best_tiebreak):
            best_val = val
            best_tiebreak = min_self_d
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]