def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d): 
        return abs(a - c) + abs(b - d)

    target = None
    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources we're significantly closer to; then closest distance; then deterministic tie by coords
            key = (od - sd, -sd, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        target = best[1] if best else None

    if target is None:
        # No usable resources: drift to a corner opposite-ish opponent
        tx = 0 if ox >= w / 2 else w - 1
        ty = 0 if oy >= h / 2 else h - 1
        target = (tx, ty)

    tx, ty = target
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Move to reduce distance to target; avoid stepping closer to opponent if tie
            d_self = man(nx, ny, tx, ty)
            d_opp = man(nx, ny, ox, oy)
            # Deterministic tie-breaking by (dx,dy) preference order
            key = (-d_self, -d_opp, -dx, -dy)
            candidates.append((key, dx, dy))
    if candidates:
        candidates.sort(reverse=True, key=lambda t: (t[0][0], t[0][1], t[0][2], t[0][3]))
        return [candidates[0][1], candidates[0][2]]
    # If blocked, try staying; engine accepts it
    return [0, 0]