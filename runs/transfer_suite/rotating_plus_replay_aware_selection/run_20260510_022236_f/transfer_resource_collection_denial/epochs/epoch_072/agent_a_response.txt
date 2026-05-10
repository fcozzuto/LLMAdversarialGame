def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    tr = int(observation.get("turns_remaining", 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid_res = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if inb(rx, ry) and (rx, ry) not in obs:
            valid_res.append((rx, ry))
    if not valid_res:
        return [0, 0]

    # Choose a resource we can win: maximize (opponent_distance - self_distance),
    # then prefer those reachable within turns; tie-break by closer distance.
    best = None
    best_key = None
    for rx, ry in valid_res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        advantage = do - ds
        reachable = 1 if tr == 0 or ds <= tr else 0
        # If opponent is already closer, allow only slightly unless it's very advantageous in margin
        # (prevents dithering in opponent's "denial" pattern).
        key = (reachable, advantage, -ds, -cheb(ox, oy, sx, sy))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    # Determine a preferred step toward the target (8-neighborhood including stay).
    dx = 0
    if rx > sx:
        dx = 1
    elif rx < sx:
        dx = -1
    dy = 0
    if ry > sy:
        dy = 1
    elif ry < sy:
        dy = -1

    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if mx == 0 and my == 0:
                pass
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            # Prefer moves that reduce distance to target; deterministic tie-break by closer to target,
            # then prefer aligning with main direction (mx,my closer to dx,dy).
            dcur = cheb(sx, sy, rx, ry)
            dnext = cheb(nx, ny, rx, ry)
            dist_gain = dcur - dnext
            align = -(abs(mx - dx) + abs(my - dy))
            # Secondary tie-break: also don't walk into squares that make opponent "too" close.
            # (still deterministic, and uses observation positions only)
            risk = cheb(ox, oy, nx, ny) - cheb(ox, oy, sx, sy)
            key = (dist_gain, align, risk, -abs(nx - rx) - abs(ny - ry))
            candidates.append((key, [mx, my]))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0], reverse=True)
    return candidates[0][1]