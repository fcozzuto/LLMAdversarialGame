def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer moves that create a clear "lead" on some resource; otherwise head to nearest safe.
    best = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # small deterministic tie-break: closer to center of map
        center_bias = - (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))

        top = -10**9
        for rx, ry in resources:
            d_self = man((nx, ny), (rx, ry))
            d_opp = man((ox, oy), (rx, ry))
            # lead strength: collect sooner than opponent
            lead = d_opp - d_self
            # resource value proxy: closer self is better
            value = lead * 10 - d_self + center_bias
            if value > top:
                top = value

        # Also penalize being too close to any obstacle (avoid traps)
        obs_pen = 0
        for ox2, oy2 in obstacles:
            md = abs(nx - ox2) + abs(ny - oy2)
            if md == 0:
                obs_pen -= 1000
            elif md == 1:
                obs_pen -= 2

        val = top + obs_pen

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]