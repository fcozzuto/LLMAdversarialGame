def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        # Drift toward center to avoid wasting time; pick deterministic axis
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Choose a target resource where we have distance advantage; break ties deterministically
    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer positive advantage; then closer overall; then lex for determinism
        key = (do - ds, -ds, rx, ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Evaluate possible moves: prefer getting closer to target while maintaining/creating advantage
    best_move = (None, None)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        ds2 = man(nx, ny, tx, ty)
        do2 = man(ox, oy, tx, ty)
        # Prefer smaller distance to target; prefer larger advantage; small tie-bias toward staying stable
        adv = do2 - ds2
        # Also avoid stepping into cells that are "too close" to an obstacle (minor)
        near_obs = 0
        for oxp, oyp in obs:
            if abs(nx - oxp) <= 1 and abs(ny - oyp) <= 1:
                near_obs += 1
        key = (adv, -ds2, -near_obs, -abs(dx) - abs(dy), dx, dy)
        if best_move[0] is None or key > best_move[0]:
            best_move = (key, [dx, dy])

    if best_move[1] is not None:
        return best_move[1]

    # Fallback: pick any in-bounds move deterministically
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny):
            return [dx, dy]
    return [0, 0]