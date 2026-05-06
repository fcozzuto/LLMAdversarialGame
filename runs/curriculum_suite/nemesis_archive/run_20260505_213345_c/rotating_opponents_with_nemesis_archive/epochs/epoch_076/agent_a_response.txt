def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_step_to_resource(r):
        # Prefer steps that make me relatively closer to r than opponent.
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h:
                    continue
                if (nx, ny) in obstacles:
                    continue
                myd = manh((nx, ny), r)
                opd = manh((ox, oy), r)
                # Smaller is better; break ties deterministically by move order.
                key = (myd - opd, myd, nx, ny)
                if best is None or key < best[0]:
                    best = (key, (dx, dy))
        return best[1] if best is not None else (0, 0)

    # First choose a "contested" target: opponent is near it, and I'm not too far.
    # This shifts behavior away from pure nearest-resource chasing.
    best_target = None
    best_key = None
    for r in resources:
        myd = manh((sx, sy), r)
        opd = manh((ox, oy), r)
        # Want to catch what opponent is approaching, but only if we have a plausible race advantage.
        key = (opd - myd, opd, myd, r[0], r[1])  # lower => better contested target
        if best_key is None or key < best_key:
            best_key = key
            best_target = r

    dx, dy = best_step_to_resource(best_target)
    return [dx, dy]