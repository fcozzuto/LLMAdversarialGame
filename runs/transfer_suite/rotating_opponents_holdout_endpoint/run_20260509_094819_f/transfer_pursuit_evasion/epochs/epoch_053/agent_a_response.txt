def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = str(observation.get("self_role") or "")
    is_pursuer = ("purs" in role.lower()) or (role.lower() == "pursuer")

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if is_pursuer:
        # Predict evader corner target: the corner maximizing distance from us.
        tx, ty = max(corners, key=lambda c: (cheb(c[0], c[1], sx, sy), -c[0], -c[1]))
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_to_evader = cheb(nx, ny, ox, oy)
            d_to_target = cheb(nx, ny, tx, ty)
            # Lower distance to evader is primary; bias toward the predicted target corner.
            v = (-d_to_evader * 1000) - d_to_target
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Evader: run to a farthest corner, but stay reachable with minimal accidental closeness.
    # Also avoid choosing the corner aligned with opponent if a tie.
    tx, ty = max(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), -c[0], -c[1]))
    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_f = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, tx, ty)
        # Max distance from pursuer primary; then increase progress toward far corner.
        v = d_f * 1000 - d_corner
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]