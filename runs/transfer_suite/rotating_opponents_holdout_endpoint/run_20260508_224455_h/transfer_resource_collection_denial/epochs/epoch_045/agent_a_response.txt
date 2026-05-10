def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    if not resources:
        return [0, 0]

    w = int(observation["grid_width"]); h = int(observation["grid_height"])

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = sorted(moves, key=lambda d: (d[0] == 0 and d[1] == 0, d[0], d[1]))

    def best_target():
        # Prefer resources we can reach no later than opponent; then minimize our distance; then deterministic.
        best = None
        for rx, ry in sorted(resources, key=lambda p: (p[0], p[1])):
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # If we can arrive earlier or tie, strong; else allow but weaker.
            earlier = 0 if ds <= do else 1
            key = (earlier, ds, -do, rx, ry)
            if best is None or key < best:
                best = key
        return best[3], best[4]

    tx, ty = best_target()

    # Evaluate immediate moves by how they improve our advantage towards the chosen target,
    # with fallback to any resource if target is blocked.
    target_blocked = (tx, ty) in obstacles
    if target_blocked:
        candidates = [p for p in resources if (p[0], p[1]) not in obstacles]
        if not candidates:
            return [0, 0]
        best = None
        for rx, ry in sorted(candidates, key=lambda p: (p[0], p[1])):
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            key = (0 if ds <= do else 1, ds, rx, ry)
            if best is None or key < best:
                best = key
        tx, ty = best[2], best[3]

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        # If move goes into obstacle, agent stays (engine keeps in place). Model that.
        if (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Compute nearest resource distance and capture advantage next turn.
        # Small lookahead: pick best among resources from the next position.
        best_next = None
        for rx, ry in sorted(resources, key=lambda p: (p[0], p[1])):
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            do = man(ox if (ox, oy) else ox, oy if (ox, oy) else oy, rx, ry)
            earlier = 0 if ds <= do else 1
            # Encourage getting onto/near target quickly, avoid being stuck.
            tie_break = 0 if (rx, ry) == (tx, ty) else 1
            val = (earlier, ds, tie_break, rx, ry)
            if best_next is None or val < best_next:
                best_next = val

        # Secondary objective: reduce distance to chosen target strongly.
        ds_t = man(nx, ny, tx, ty)
        do_t = man(ox, oy, tx, ty)
        earlier_t = 0 if ds_t <= do_t else 1
        stuck_pen = 1 if (nx, ny) == (sx, sy) else 0
        current = (best_next, earlier_t, ds_t, stuck_pen, dx, dy)
        if best_val is None or current < best_val:
            best_val = current
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]