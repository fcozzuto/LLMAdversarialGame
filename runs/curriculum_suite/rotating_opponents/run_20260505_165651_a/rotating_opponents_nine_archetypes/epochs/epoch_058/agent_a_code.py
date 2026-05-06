def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obstacles)

    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    def eval_resource(rx, ry):
        d_me = man(sx, sy, rx, ry)
        d_op = man(ox, oy, rx, ry)
        # prefer nearer, and prefer resources where we can arrive first (or close)
        ahead = d_op - d_me
        return (d_me - 0.45 * ahead) + (0.08 * (d_op))

    if resources:
        # pick up to a few closest candidates for efficiency/determinism
        resources_sorted = sorted(resources, key=lambda p: eval_resource(p[0], p[1]))
        candidates = resources_sorted[:6] if len(resources_sorted) > 6 else resources_sorted
    else:
        candidates = []

    # If no resources, move toward center while keeping distance from opponent
    if not candidates:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_move = [0, 0]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            key = (man(nx, ny, cx, cy), man(ox, oy, nx, ny), dx, dy)
            if best is None or key < best:
                best, best_move = key, [dx, dy]
        return best_move

    # Otherwise choose move that best improves our progress toward the best contested resource
    best_key = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        # avoid ending up too close to opponent unless it helps contest a resource
        opp_dist = man(nx, ny, ox, oy)

        # compute best target after this move
        best_target = None
        best_target_val = None
        for rx, ry in candidates:
            d_me = man(nx, ny, rx, ry)
            d_op = man(ox, oy, rx, ry)
            ahead = d_op - d_me
            # if opponent is significantly closer, de-prioritize unless we still get very close
            val = d_me - 0.55 * ahead + 0.10 * d_op
            # slight preference to reduce our distance to opponent if we can contest (ahead >= 0)
            if ahead >= 0:
                val -= 0.05 * opp_dist
            if best_target_val is None or val < best_target_val:
                best_target_val = val
                best_target = (rx, ry)

        rx, ry = best_target
        d_me_now = man(nx, ny, rx, ry)
        d_op_now = man(ox, oy, rx, ry)
        # tie-break: prefer moves that increase our arrival advantage and keep some separation
        key = (best_target_val, -(d_op_now - d_me_now), -opp_dist, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move