def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [W - 1, H - 1])
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    valid_res = [(r[0], r[1]) for r in resources if r and len(r) >= 2 and ok(r[0], r[1])]
    if not valid_res:
        tx, ty = (W - 1) if (sx < W // 2) else 0, (H - 1) if (sy < H // 2) else 0
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = max(abs(nx - tx), abs(ny - ty))
            if best is None or d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [best[1], best[2]]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Change: interception rather than greedy chase.
    # For each step, score by best achievable "lead" against any resource:
    # minimize (our_distance - opp_distance) (more negative is better), plus tie-breakers.
    best_step = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_lead = None
        best_dist_opp = None
        best_dist_us = None
        best_res = None
        for rx, ry in valid_res:
            du = man((nx, ny), (rx, ry))
            do = man((ox, oy), (rx, ry))
            lead = du - do
            # Prefer resources where we can arrive no later than opponent, then closest to that resource.
            if best_lead is None or lead < best_lead or (lead == best_lead and (du < best_dist_us)) or (lead == best_lead and du == best_dist_us and (do < best_dist_opp)) or (lead == best_lead and du == best_dist_us and do == best_dist_opp and (rx, ry) < best_res):
                best_lead, best_dist_us, best_dist_opp, best_res = lead, du, do, (rx, ry)
        # Additionally discourage moving away from opponent's target by adding small penalty on our absolute closeness to that resource.
        # (deterministic, still based on best_res chosen above)
        rx, ry = best_res
        penalty = 0
        if (nx, ny) == (sx, sy):
            penalty = 1  # slight preference to not stand still
        score = (best_lead, best_dist_us, best_dist_opp, penalty, dx, dy)
        if best_step is None or score < best_step[0]:
            best_step = (score, dx, dy)

    return [best_step[1], best_step[2]]