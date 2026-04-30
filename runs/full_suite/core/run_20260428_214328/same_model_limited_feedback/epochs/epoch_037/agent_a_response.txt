def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if w is None: w = 8
    if h is None: h = 8

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) / 2, (h - 1) / 2
        cand = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    dd = cheb(nx, ny, tx, ty)
                    cand.append((dd, -cheb(nx, ny, ox, oy), dx, dy))
        cand.sort()
        return [cand[0][2], cand[0][3]] if cand else [0, 0]

    best = None
    for rx, ry in resources:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach no later, but when none, grab closest to deny.
        score = (0, dS) if dS <= dO else (1, -dO, dS)
        if best is None or score < best[0] or (score == best[0] and (dS < best[1])):
            best = (score, dS, rx, ry)

    _, _, tx, ty = best
    opts = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d1 = cheb(nx, ny, tx, ty)
                # Tie-break: move away from opponent to reduce contest pressure.
                d2 = cheb(nx, ny, ox, oy)
                # Lexicographic tie-break on (dx, dy) via ordering.
                opts.append((d1, -d2, dx, dy))
    if not opts:
        return [0, 0]
    opts.sort()
    return [opts[0][2], opts[0][3]]