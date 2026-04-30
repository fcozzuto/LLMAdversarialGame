def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in moves:
            v = cheb(nx, ny, tx, ty) + 0.5 * cheb(nx, ny, ox, oy)
            if best is None or v < best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    obs_center = cheb(sx, sy, cx, cy)
    best_move = None
    best_val = None

    # Deterministic resource ordering: center-first, then opponent urgency, then coords
    ordered = sorted(resources, key=lambda r: (cheb(r[0], r[1], cx, cy), cheb(ox, oy, r[0], r[1]), r[0], r[1]))
    ordered = ordered[:8]

    for dx, dy, nx, ny in moves:
        # Prefer moves that create the biggest "lead" to the next resource we can plausibly race for.
        local_best = None
        for rx, ry in ordered:
            dme = cheb(nx, ny, rx, ry)
            dob = cheb(ox, oy, rx, ry)

            # Lead score: positive means we're closer than opponent.
            lead = dob - dme

            # Encourage reaching resources sooner, discourage giving up immediate race.
            # Also lightly prefer resources that keep us progressing toward the center.
            v = -dme + 1.7 * lead - 0.12 * cheb(nx, ny, cx, cy)

            # If we can secure a resource while opponent is also far, value it more.
            if lead > 0:
                v += 0.25 * (lead if lead < 6 else 6)

            if local_best is None or v > local_best:
                local_best = v

        # Strategic mode change: if we're far from center or trailing, bias toward the closest lead
        # (different than always shortest path; this reacts to being behind).
        mode_trailing = cheb(sx, sy, ox, oy) < 3 or cheb(sx, sy, resources[0][0], resources[0][1]) > 4
        bias = 0.35 * (cheb(nx, ny, cx, cy) - obs_center)
        if mode_trailing:
            bias = 0.15 * cheb(nx, ny, cx, cy)

        val = local_best - bias
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [best_move[0], best_move[1]]