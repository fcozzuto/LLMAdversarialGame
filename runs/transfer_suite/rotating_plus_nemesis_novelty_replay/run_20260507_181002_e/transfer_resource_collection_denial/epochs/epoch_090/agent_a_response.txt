def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [sx, sy])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Precompute top resource candidates by my current distance (small, deterministic)
    resources_sorted = sorted(resources, key=lambda p: man(sx, sy, p[0], p[1]))
    top = resources_sorted[: min(8, len(resources_sorted))]

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # For this move, aim for the resource where we get the best lead over opponent
        local_best = -10**18
        for tx, ty in top:
            myd = man(nx, ny, tx, ty)
            oppd = man(ox, oy, tx, ty)
            # Positive means lead; tie-break favors shorter my path and longer opponent path
            score = (oppd - myd) * 100 - myd - 0.01 * oppd
            if score > local_best:
                local_best = score
        # If we're stuck adjacent to obstacles, allow choosing least-bad move
        if local_best == -10**18:
            local_best = -man(nx, ny, top[0][0], top[0][1])
        # Encourage not worsening our situation relative to current position
        cur_best = -10**18
        for tx, ty in top:
            myd = man(sx, sy, tx, ty)
            oppd = man(ox, oy, tx, ty)
            cur_best = max(cur_best, (oppd - myd) * 100 - myd - 0.01 * oppd)
        delta = local_best - cur_best
        final_score = local_best + (1.5 if delta >= 0 else -0.5) * abs(delta)
        if final_score > best_score or (final_score == best_score and (dx, dy) < best_move):
            best_score = final_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]