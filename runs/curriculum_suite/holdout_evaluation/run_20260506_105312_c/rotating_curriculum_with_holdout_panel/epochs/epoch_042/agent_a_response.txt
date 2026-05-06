def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    if not resources:
        return [0, 0]

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                cand.append((nx, ny, dx, dy))
    if not cand:
        return [0, 0]

    # Pick resources that we are closer to than opponent; otherwise still choose best tradeoff.
    best = None
    bestv = -10**18
    for nx, ny, dx, dy in cand:
        # discourage sticking too close to opponent
        base = cheb(nx, ny, ox, oy)
        score = base * 0.25
        my_best = 10**9
        opp_best_for_me = -10**9

        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            my_best = md if md < my_best else my_best
            # If we are leading on a resource, prioritize it strongly; if not, deprioritize.
            lead = od - md  # positive means we are closer than opponent
            if lead >= 0:
                v = 1000 * lead - 10 * md
            else:
                v = 40 * lead - 6 * md  # still consider but less
            # Also slightly prefer resources that are more contested away from opponent.
            contested = (md + od)
            v -= 2 * contested * (1 if lead < 0 else 0)
            # Give a small extra preference to nearer-to-them-leading resources.
            if md < 6:
                v += 6
            score += v
            if lead > opp_best_for_me:
                opp_best_for_me = lead

        # Additional deterministic nudge: if we are not leading any resource, head toward the closest resource.
        if opp_best_for_me < 0:
            score -= 30 * my_best

        # Tie-break deterministically: prefer staying still less, then smaller dx,dy ordering.
        score2 = score - (1 if (dx != 0 or dy != 0) else 0) * 0.001 - (dx * 0.0001) - (dy * 0.00001)

        if score2 > bestv:
            bestv = score2
            best = (dx, dy)

    return [int(best[0]), int(best[1])]