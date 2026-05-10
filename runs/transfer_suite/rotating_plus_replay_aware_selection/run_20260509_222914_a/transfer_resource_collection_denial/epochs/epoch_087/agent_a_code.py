def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # Deterministic tie-breaking: fixed order by (best_adv desc, best_self_dist asc, best_opp_dist asc, move index asc)
    best = None
    best_move = [0, 0]

    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # "Racing" score: prioritize resources where we are closer than opponent.
        # Use a robust aggregate: best (maximum) advantage among top few closest targets.
        scored = []
        for (rx, ry) in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - self_d
            scored.append((adv, self_d, opp_d, rx, ry))
        # Pick top K by advantage then closeness for determinism (small K to stay cheap)
        scored.sort(key=lambda t: (-t[0], t[1], t[2], t[3], t[4]))
        K = 5 if len(scored) >= 5 else len(scored)
        top = scored[:K]

        # Combine: strongest advantage, then reduce self distance to the first target
        adv_max = top[0][0]
        self_dist_0 = top[0][1]
        opp_dist_0 = top[0][2]

        # Mild density nudge: count nearby resources around our prospective position
        nearby = 0
        for (rx, ry) in resources:
            if man(nx, ny, rx, ry) <= 2:
                nearby += 1

        key = (adv_max, -nearby, -len([t for t in top if t[0] > 0]), -top[0][1], -top[0][2], -i)
        # key comparisons: we want adv_max high; for other parts we've encoded directions in key
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]