def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obs = {(p[0], p[1]) for p in obstacles}

    if not resources:
        dx, dy = 0, 0
        # Move to increase distance from opponent
        best = (-10**9, (0, 0))
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                nx, ny = sx + ddx, sy + ddy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                    score = abs(nx - ox) + abs(ny - oy)
                    if score > best[0]:
                        best = (score, (ddx, ddy))
        return [best[1][0], best[1][1]]

    # Opponent-aware target selection: pick resource where we have the largest distance advantage.
    def md(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    best_res = None
    best_adv = -10**18
    for r in resources:
        rxy = (r[0], r[1])
        sd = md((sx, sy), rxy)
        od = md((ox, oy), rxy)
        adv = (od - sd) * 10 - 0.1 * (sd + od)
        # Prefer safer/closer options when tied
        if (rxy not in obs) and (adv > best_adv or (adv == best_adv and sd < md((sx, sy), (best_res[0], best_res[1])))):
            best_adv = adv
            best_res = (rxy[0], rxy[1])

    tx, ty = best_res

    # Choose immediate move that reduces distance to target, with tie-breaks: avoid opponent and obstacles.
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = -10**18
    best_move = (0, 0)
    for ddx, ddy in candidates:
        nx, ny = sx + ddx, sy + ddy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        dist_to_t = abs(nx - tx) + abs(ny - ty)
        dist_to_o = abs(nx - ox) + abs(ny - oy)
        # If target is adjacent/opponent is close, prioritize moving away slightly to avoid contest losses.
        contest = -md((ox, oy), (tx, ty))
        score = (-dist_to_t * 20) + (dist_to_o * 0.5) + contest * 0.01
        if score > best_score:
            best_score = score
            best_move = (ddx, ddy)

    # If all candidate moves are blocked/out of bounds, stay.
    return [int(best_move[0]), int(best_move[1])]