def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        v1 = a - c
        if v1 < 0:
            v1 = -v1
        v2 = b - d
        if v2 < 0:
            v2 = -v2
        return v1 + v2

    if not resources:
        return [0, 0]

    # Determine a deterministic "front" resource to contest
    # Prefer nearest to us, but only consider those where we are not far behind opponent.
    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Lower is better: we want small ds, and large (do-ds) if possible
        key = (ds, do - ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    rx, ry = best_target
    remaining = observation.get("remaining_resource_count")
    try:
        remaining = int(remaining) if remaining is not None else len(resources)
    except:
        remaining = len(resources)

    # When resources are few, prioritize closing quickly; otherwise blend contesting.
    contest_weight = 2.0 if remaining <= 5 else 1.0
    speed_weight = 3.0 if remaining <= 5 else 2.0

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        ds = man(nx, ny, rx, ry)
        do = man(ox, oy, rx, ry)

        # Multi-resource hint: also slightly prefer states that reduce our best remaining distance.
        min_other = 10**9
        for (rrx, rry) in resources:
            d = man(nx, ny, rrx, rry)
            if d < min_other:
                min_other = d

        # Score: prioritize being closer to target, and not letting opponent be too far ahead.
        # Add tie-breakers deterministically to avoid oscillation.
        ahead = do - ds
        score = (speed_weight * ds - contest_weight * ahead + 0.1 * min_other, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]