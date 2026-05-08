def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1),(0, -1),(1, -1),(-1, 0),(0, 0),(1, 0),(-1, 1),(0, 1),(1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Pick a deterministic target: maximize opponent distance advantage (opp closer => worse for us).
    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds
        key = (adv, -ds, -do, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    if best is None:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    rx, ry = best[1]
    base_do = man(ox, oy, rx, ry)

    # Choose next move greedily toward target, but keep maximizing our distance advantage.
    best_move = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy  # engine keeps us in place; keep evaluation consistent

        my_next = man(nx, ny, rx, ry)
        adv_next = base_do - my_next
        # Small preference for moves that don't give opponent an immediate stealing edge (increase their distance)
        opp_next = base_do  # unknown; approximate using current only
        # Prefer increasing distance from opponent to reduce contention
        dist_opp = man(nx, ny, ox, oy)
        key = (adv_next, -my_next, dist_opp, dx, dy, opp_next)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move