def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    def min_dist_to_resources(x, y):
        md = 10**9
        for rx, ry in resources:
            d = abs(rx - x) + abs(ry - y)
            if d < md:
                md = d
        return md

    # If we are adjacent to a resource, prioritize it by moving toward it.
    immediate_targets = []
    for rx, ry in resources:
        if abs(rx - sx) <= 1 and abs(ry - sy) <= 1:
            immediate_targets.append((rx, ry))
    if immediate_targets:
        # Deterministically pick the target with smallest opponent advantage (prefer equal/ours).
        tx, ty = immediate_targets[0]
        best_pair = None
        for rx, ry in immediate_targets:
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            key = (do - ds, -(abs(rx - ox) + abs(ry - oy)))
            if best_pair is None or key > best_pair:
                best_pair = key
                tx, ty = rx, ry
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        # If blocked, fall through to normal scoring.
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]

    # Main: evaluate each legal move by resource competitiveness + row contest.
    md_now = min_dist_to_resources(sx, sy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Resource competitiveness: choose best resource for us from the new position.
        local_best = -10**18
        local_ds = 10**9
        for rx, ry in resources:
            ds = abs(rx - nx) + abs(ry - ny)
            do = abs(rx - ox) + abs(ry - oy)
            # Prefer resources we can reach sooner than opponent.
            base = (do - ds)
            # Contest opponent sweep: align with their current row (and slight col).
            contest = 2.0 if ry == oy else 0.0
            align = 0.5 if rx == ox else 0.0
            # Encourage progress.
            progress = 0.15 * (md_now - ds)
            # Slight preference for closer resources (fewer steps).
            closeness = -0.03 * ds
            score = base + contest + align + progress + closeness
            if score > local_best or (score == local_best and ds < local_ds):
                local_best = score
                local_ds = ds

        # Tie-break: avoid moving away overall.
        penalty_away = 0.01 * (local_ds - md_now) if local_ds > md_now else 0.0
        val = local_best - penalty_away

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]