def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    obs_set = set((a, b) for a, b in obstacles)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        # No visible resources: drift toward opponent's corner to contest space.
        tx = w - 1 if sx < w - 1 else 0
        ty = h - 1 if sy < h - 1 else 0
        target = (tx, ty)
    else:
        # Pick resource that is closest to us but far from opponent.
        best = None
        for rx, ry in resources:
            da = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Slight preference for nearer resources; strong preference for keeping opponent distance.
            key = (-(da) + 0.35 * (do), -da, do, rx, ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        target = best[1]

    tx, ty = target
    cur_on_resource = (sx, sy) in set((a, b) for a, b in resources)

    best_move = (0, 0)
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue

        # Prefer stepping onto a resource.
        on_res = (nx, ny) in set((a, b) for a, b in resources)
        d_to_t = dist(nx, ny, tx, ty)
        d_to_o = dist(nx, ny, ox, oy)

        # If we already stand on a resource, try not to leave it unless it improves dramatically.
        leave_pen = 0
        if cur_on_resource and not on_res:
            leave_pen = 5

        # Greedy approach with opponent-awareness.
        val = (1000 if on_res else 0) + (-d_to_t) + 0.25 * d_to_o - leave_pen
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            # Deterministic tie-break: prefer moves with smaller |dx|+|dy| then lexicographic dx,dy.
            if (abs(dx) + abs(dy), dx, dy) < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1]):
                best_move = (dx, dy)

    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]