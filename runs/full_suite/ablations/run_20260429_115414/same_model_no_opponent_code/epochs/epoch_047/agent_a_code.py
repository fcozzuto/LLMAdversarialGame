def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort(key=lambda t: (t[0], t[1]))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Choose target resource by deterministic nearest (Chebyshev); if tie, lexicographic.
    if res:
        best_target = res[0]
        best_td = cheb(sx, sy, best_target[0], best_target[1])
        for r in res[1:]:
            td = cheb(sx, sy, r[0], r[1])
            if td < best_td or (td == best_td and (r[0], r[1]) < (best_target[0], best_target[1])):
                best_td = td
                best_target = r
        tx, ty = best_target
    else:
        tx, ty = ox, oy  # no resources visible; neutralize by holding position (tie-break later)

    # Score candidate moves: prefer shortest to target, then prefer being farther from opponent,
    # and finally deterministic tie-break by move ordering.
    best = (10**18, -10**18, 0, 0)
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        td = cheb(nx, ny, tx, ty)
        od = cheb(nx, ny, ox, oy)
        # primary: minimize td; secondary: maximize od (avoid close contest); tertiary: stay/lex by move
        cand = (td, -od, dx, dy)
        if cand < best:
            best = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]