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

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Pick target deterministically: minimize (our_dist - opp_dist), then our_dist, then lex
    tx, ty = w // 2, h // 2
    if resources:
        best_key = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = r[0], r[1]
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            key = (ds - do, ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                tx, ty = rx, ry

    # If enemy is extremely close to our chosen target, try to "swerve" to another best we can beat
    if resources:
        dso = man(ox, oy, tx, ty)
        if dso <= 1:
            best_key = None
            for r in resources:
                if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                    continue
                rx, ry = r[0], r[1]
                ds = man(sx, sy, rx, ry)
                do = man(ox, oy, rx, ry)
                key = (ds - do, ds, rx, ry)
                if best_key is None or key < best_key:
                    best_key = key
                    tx, ty = rx, ry

    # Step toward target with tie-break: avoid moving away, then minimize distance to target, then lex of move
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        cur = man(sx, sy, tx, ty)
        nxt = man(nx, ny, tx, ty)
        # prefer non-increasing distance; then smallest next distance; then smallest move delta lex
        key = (1 if nxt > cur else 0, nxt, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]