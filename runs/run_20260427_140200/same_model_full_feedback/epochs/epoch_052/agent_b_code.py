def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        ax -= bx
        if ax < 0: ax = -ax
        ay -= by
        if ay < 0: ay = -ay
        return ax + ay

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if resources:
            local_best = -10**18
            for rx, ry in resources:
                myd = man(nx, ny, rx, ry)
                opd = man(ox, oy, rx, ry)
                # Prefer resources we are closer to than opponent; tie-break by shorter my distance.
                value = (opd - myd) * 10.0 - myd * 1.2
                # Small bias toward board center to stabilize paths.
                value -= ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.03
                if value > local_best:
                    local_best = value
            score = local_best
        else:
            # No visible resources: move toward center while keeping safe.
            score = -(((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) + man(nx, ny, ox, oy) * 0.15)

        # Deterministic tie-break: prefer staying still less? prefer lexicographically smaller move.
        if score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score and best is not None:
            if (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]