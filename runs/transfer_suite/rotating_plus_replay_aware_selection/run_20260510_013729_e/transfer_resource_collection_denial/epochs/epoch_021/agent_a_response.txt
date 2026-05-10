def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obstacle_set = {(x, y) for x, y in obstacles}

    def cheb(x1, y1, x2, y2):
        a = x2 - x1
        if a < 0:
            a = -a
        b = y2 - y1
        if b < 0:
            b = -b
        return a if a > b else b

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Pick target by strongest advantage; if tie, pick closest, then deterministic id.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (do - ds, -ds, -(rx * 8 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacle_set:
            continue

        # Primary: maximize improvement in arrival advantage to chosen target.
        ds_now = cheb(sx, sy, tx, ty)
        do_now = cheb(ox, oy, tx, ty)
        ds_next = cheb(nx, ny, tx, ty)
        do_next = do_now  # opponent moves independently; keep local estimate consistent

        adv_now = do_now - ds_now
        adv_next = do_next - ds_next

        # Secondary: prefer moves that reduce distance to target; avoid standing still if a better cell exists.
        dist_next = ds_next

        # Tertiary: slight repulsion from obstacles (deterministic) to reduce future collisions.
        rep = 0
        for ax, ay in obstacles:
            dd = cheb(nx, ny, ax, ay)
            if dd == 0:
                rep -= 100
            else:
                rep -= 1.0 / (dd + 1)

        score = (adv_next - adv_now) * 1000 + (-dist_next) + rep

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: prefer smaller (dx,dy) lexicographically
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]