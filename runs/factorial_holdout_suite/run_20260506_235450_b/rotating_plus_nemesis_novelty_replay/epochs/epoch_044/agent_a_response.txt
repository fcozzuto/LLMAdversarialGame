def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w - 1, h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for mx, my in cand:
            if valid(sx + mx, sy + my):
                return [mx, my]
        return [0, 0]

    # Collects worth more: prioritize cells that are "safer" against opponent by advantage.
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Small deterministic tie-break to reduce dithering.
    order = {(-1, -1): 0, (0, -1): 1, (1, -1): 2, (-1, 0): 3, (0, 0): 4, (1, 0): 5, (-1, 1): 6, (0, 1): 7, (1, 1): 8}

    best_score = None
    best_move = (0, 0)

    # If already on a resource, stay; otherwise compute best step.
    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate best target from this hypothetical position.
        # Score tuple: (advantage, -self_dist, target_index) where larger advantage is better.
        local_best = None
        for i, (rx, ry) in enumerate(resources):
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer targets we can reach not later than opponent; penalize losing races.
            adv = od - sd
            # Slight bonus if both race equally (tie-break by earlier approach): smaller sd preferred.
            tie_bonus = 0 if adv != 0 else (1000 - sd)
            sc = (adv, tie_bonus - sd, -i)  # higher better
            if local_best is None or sc > local_best:
                local_best = sc

        # Also encourage moving into the direction of the chosen target by implicit distance component.
        if local_best is None:
            continue

        # Secondary: don't get trapped near obstacles; discourage adjacency to obstacles a bit.
        # (Deterministic, cheap)
        adj_pen = 0
        for ax, ay in cand:
            tx, ty = nx + ax, ny + ay
            if inb(tx, ty) and (tx, ty) in obs:
                adj_pen += 1

        final = (local_best[0], local_best[1], -adj_pen, -order[(dx, dy)])
        if best_score is None or final > best_score:
            best_score = final
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]