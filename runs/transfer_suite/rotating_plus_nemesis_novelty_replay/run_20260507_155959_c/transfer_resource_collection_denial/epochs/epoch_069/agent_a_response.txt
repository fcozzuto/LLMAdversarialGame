def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (nx, ny) == (sx, sy):
                continue
            if inb(nx, ny) and (nx, ny) not in obs:
                valid.append((dx, dy))
    valid.append((0, 0))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = r[0], r[1]
            if not inb(rx, ry) or (rx, ry) in obs:
                continue
            ds = man((sx, sy), (rx, ry))
            do = man((ox, oy), (rx, ry))
            adv = do - ds  # positive: we're closer
            key = (adv, -ds, rx, ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        if best is not None:
            tx, ty = best[1]
            best_move = (0, None)
            for dx, dy in valid:
                nx, ny = sx + dx, sy + dy
                d = man((nx, ny), (tx, ty))
                # prioritize reducing distance; deterministic tie-break by movement
                key = (-d, abs(dx) + abs(dy), dx, dy)
                if best_move[1] is None or key > best_move[0]:
                    best_move = (key, (dx, dy))
            return [best_move[1][0], best_move[1][1]]

    # No usable resources: drift toward center of remaining reachable region
    cx, cy = w // 2, h // 2
    best_move = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d = man((nx, ny), (cx, cy))
        key = (-d, abs(dx) + abs(dy), dx, dy)
        if best_move is None or key > best_move[0]:
            best_move = (key, (dx, dy))
    return [best_move[1][0], best_move[1][1]]