def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (-(10**9), 10**9, 10**9)
    best_move = [0, 0]

    # Deterministic: evaluate all legal moves, score by (advantage, closeness, avoid bad moves)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        # advantage: how much closer we are than opponent to the same resource
        top_adv = -(10**9)
        top_myd = 10**9
        top_opd = 10**9
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = opd - myd
            # Prefer large advantage; if tied, prefer smaller myd; if still tied, prefer larger myd (less risk)?? keep stable
            if adv > top_adv or (adv == top_adv and myd < top_myd):
                top_adv, top_myd, top_opd = adv, myd, opd

        # Additional robust term: if we can already be first next step, prioritize those even more.
        # next_pick_bonus encourages moving onto resources that are closest to us.
        next_pick_bonus = 0
        if top_myd == 0:
            next_pick_bonus = 50
        elif top_myd == 1:
            next_pick_bonus = 10

        # Penalty for moving away from the currently best resource direction (helps stability vs oscillation)
        # Choose a reference resource: the resource where opponent is currently closest (most threatening).
        ref_opd = 10**9
        ref_rx, ref_ry = resources[0]
        for rx, ry in resources:
            opd0 = man(ox, oy, rx, ry)
            if opd0 < ref_opd:
                ref_opd = opd0
                ref_rx, ref_ry = rx, ry
        dist_ref_before = man(sx, sy, ref_rx, ref_ry)
        dist_ref_after = man(nx, ny, ref_rx, ref_ry)
        away_pen = dist_ref_after - dist_ref_before  # positive => we moved away

        score = (top_adv + next_pick_bonus, top_myd, away_pen)
        # Max score lexicographically by first two, then by smaller away_pen
        if score[0] > best[0] or (score[0] == best[0] and (score[1] < best[1] or (score[1] == best[1] and score[2] < best[2]))):
            best = score
            best_move = [dx, dy]

    return best_move