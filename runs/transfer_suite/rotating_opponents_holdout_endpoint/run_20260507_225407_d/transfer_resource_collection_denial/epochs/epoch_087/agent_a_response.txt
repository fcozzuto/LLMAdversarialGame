def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    rem = observation.get("remaining_resource_count", None)
    rem = int(rem) if rem is not None else len(resources)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Prefer racing early; deny pressure later.
    race = 1.0 if rem > 6 else 1.25
    deny = 0.2 if rem > 6 else 0.75

    def obs_pen(tx, ty):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (tx + ax, ty + ay) in obstacles:
                    p += 1
        return p

    best = None
    best_key = None
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Lower is better: self advantage + obstacle penalty, with later denial emphasis.
        key = (race * sd - (1.0 + deny) * od) + 0.1 * obs_pen(tx, ty)
        tie = (sd, tx, ty)
        full = (key, tie)
        if best_key is None or full < best_key:
            best_key = full
            best = (tx, ty)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if not inb(nx, ny):
        # Clamp deterministically; try orthogonal if diagonal goes out.
        if not inb(sx + dx, sy):
            dx = 0
        if not inb(sx, sy + dy):
            dy = 0
    return [int(dx), int(dy)]