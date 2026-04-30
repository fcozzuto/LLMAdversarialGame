def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestd = 10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man(sx, sy, cx, cy) - man(nx, ny, cx, cy)
            if d > bestd:
                bestd, best = d, (dx, dy)
        return [best[0], best[1]]

    # Pick a target that we are relatively closer to than the opponent.
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer taking resources where we are closer; also break ties deterministically.
        key = (ds - 0.85 * do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key, best_r = key, (rx, ry)
    tx, ty = best_r

    # Choose a valid step that reduces distance to target; use opponent proximity to avoid obvious traps.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d_next = man(nx, ny, tx, ty)
        d_now = man(sx, sy, tx, ty)
        gain = d_now - d_next

        # Slightly discourage moving into positions where opponent gets closer to our chosen target.
        opp_d_next = man(ox, oy, tx, ty)
        # If opponent is already much closer, prioritize lateral steps by also considering distance to opponent.
        opp_to_us = man(ox, oy, nx, ny)
        score = 1000 * gain - 2 * d_next + 0.05 * opp_to_us + (1 if gain > 0 else 0) - 0.01 * opp_d_next
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score, best_move = score, (dx, dy)

    return [best_move[0], best_move[1]]