def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def step_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    if resources:
        # Prefer resources where we are at least as close as opponent; otherwise minimize our advantage deficit.
        ti = observation.get("turn_index", 0)
        best = None
        for tx, ty in resources:
            ds = man(sx, sy, tx, ty)
            do = man(ox, oy, tx, ty)
            # Lower is better: we want ds < do, and tie-break deterministically by position and turn_index.
            bias = (tx + 3 * ty + ti) % 7
            key = (ds - do, ds, bias)
            if best is None or key < best[0]:
                best = (key, tx, ty)

        _, tx, ty = best
        # Evaluate actual next move among legal options.
        best_move = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            ns = man(nx, ny, tx, ty)
            # Also discourage moving to a square where opponent becomes much closer to the same target.
            no = man(ox, oy, tx, ty)
            # Add preference for reducing distance to any other resource if we're already close.
            closest_other = ns
            for rx, ry in resources:
                if rx == tx and ry == ty:
                    continue
                closest_other = min(closest_other, man(nx, ny, rx, ry))
            val = (ns - no, ns, closest_other)
            if best_move is None or val < best_move[0]:
                best_move = (val, dx, dy)
        return [best_move[1], best_move[2]] if best_move else [0, 0]

    # No resources: drift toward the center while avoiding obstacles.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    ti = observation.get("turn_index", 0)
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        val = (man(nx, ny, cx, cy), (nx + 2 * ny + ti) % 5)
        if best is None or val < best[0]:
            best = (val, dx, dy)
    return [best[1], best[2]] if best else [0, 0]