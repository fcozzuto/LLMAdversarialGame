def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Precompute "obstacle pressure" squares (adjacent to obstacles)
    obs_adj = set()
    for ax, ay in obstacles:
        for dx, dy in moves:
            nx, ny = ax + dx, ay + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                obs_adj.add((nx, ny))

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Primary: maximize the worst-case "opponent advantage" after this move.
        # For each resource: (opd - my). Positive means we are closer (good).
        min_diff = 10**9
        min_my = 10**9
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            d = opd - myd
            if d < min_diff:
                min_diff = d
            if myd < min_my:
                min_my = myd

        # Secondary: encourage staying near contested/near resources (avoid drifting).
        # Tertiary: if we can, move toward obstacle-adjacent squares to disrupt paths.
        obs_bonus = 0
        if obs_adj:
            dist_obs = min(manhattan for manhattan in [man(nx, ny, ox2, oy2) for (ox2, oy2) in obs_adj])
            # closer to obstacle-adj gets higher bonus; capped by 8 for stability
            obs_bonus = 8 - min(8, dist_obs)

        # Lexicographic maximize: (min_diff, -min_my, obs_bonus, dx, dy)
        key = (min_diff, -min_my, obs_bonus, -dx, -dy)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]