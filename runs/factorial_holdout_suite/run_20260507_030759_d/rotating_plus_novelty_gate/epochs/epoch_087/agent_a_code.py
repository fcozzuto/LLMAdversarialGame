def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    turns_remaining = observation.get("turns_remaining", 0) or 0

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((p[0], p[1]))

    if not res:
        return [0, 0]
    if (sx, sy) in set(res):
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_opp_can = None
    opp_d_min = 10**9
    for r in res:
        d = md((ox, oy), r)
        if d < opp_d_min:
            opp_d_min = d
            best_opp_can = r

    # Generate legal moves (engine will reject invalid by staying, but we avoid it)
    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def move_value(dx, dy):
        nx, ny = sx + dx, sy + dy
        # If we land on a resource, take it.
        if (nx, ny) in set(res):
            return 10**6

        best = -10**18
        for r in res:
            sd = md((nx, ny), r)
            od = md((ox, oy), r)

            # Prefer resources we can arrive at sooner (strictly), else maximize advantage.
            # Tie-break encourages nearer resources (higher self arrival likelihood).
            advantage = od - sd
            reachable_window = 0
            if turns_remaining > 0:
                if sd <= turns_remaining:
                    reachable_window = 6
                if od <= turns_remaining:
                    reachable_window -= 3

            # If opponent is extremely close to their nearest resource, reduce allowing them to keep parity.
            focus_penalty = 0
            if best_opp_can is not None and r == best_opp_can:
                focus_penalty = -2 if advantage <= 0 else 0

            # Light penalty for not moving closer to any resource
            # (helps avoid oscillations against row-sweep behavior)
            self_dist_to_any = min(md((nx, ny), rr) for rr in res)
            closeness = -self_dist_to_any

            val = (advantage * 20) + reachable_window + focus_penalty + (sd * -1) + closeness
            if val > best:
                best = val
        return best

    # Deterministic selection: maximize value; then fixed ordering on move
    move_order = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal_set = set(legal)
    ranked = [m for m in move_order if m in legal_set]
    best_move = ranked[0]
    best_val = move_value(best_move[0], best_move[1])
    for dx, dy in ranked[1:]:
        v = move_value(dx, dy)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]