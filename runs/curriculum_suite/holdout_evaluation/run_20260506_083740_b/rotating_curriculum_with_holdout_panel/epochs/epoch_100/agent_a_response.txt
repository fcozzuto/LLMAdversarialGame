def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If no resources, move to reduce distance to opponent's likely approach: bias toward their x/y
    if not resources:
        tx = 0 if ox == sx else (1 if ox > sx else -1)
        ty = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + tx, sy + ty
        if ok(nx, ny):
            return [tx, ty]
        # fallback: any legal move
        for dx, dy in moves:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    # Precompute a few nearest resources from current positions for stable, deterministic scoring
    res_sorted_by_self = sorted(resources, key=lambda r: md(sx, sy, r[0], r[1]))
    candidates = res_sorted_by_self[:min(4, len(res_sorted_by_self))]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Main objective: deny by aiming at resources where we're not worse than opponent, but still advance.
        # Add a strong penalty if a move brings us significantly closer to a resource the opponent is already closer to.
        value = 0
        for rx, ry in candidates:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            # If opponent is closer, discouraging our approach to that cell helps denying.
            value += (do - ds) * 10
            if do < ds:
                value -= (ds - do) * 6
            # Small encouragement for actually reaching a resource quickly.
            value += max(0, 12 - ds)

        # Secondary objective: keep improving relative position vs opponent (interceptor-style).
        value += (md(ox, oy, nx, ny) * -1) + (md(ox, oy, sx, sy) - md(ox, oy, nx, ny)) * 2

        # Tertiary: stay closer to center to reduce wall/edge traps against patrol archetype.
        value += - (abs(nx - cx) + abs(ny - cy))

        # Deterministic tie-break: lexicographic on (dx,dy) favor earlier move in moves list
        if value > best[0]:
            best = (value, dx, dy)

    return [best[1], best[2]]