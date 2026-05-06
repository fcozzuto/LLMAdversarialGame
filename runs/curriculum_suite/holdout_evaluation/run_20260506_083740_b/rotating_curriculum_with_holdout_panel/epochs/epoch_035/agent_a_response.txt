def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    resources = observation.get("resources", []) or []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose target resource where we can beat opponent (or fallback to nearest)
    best = None  # (margin, self_dist, rx, ry)
    best_fallback = None  # (self_dist, rx, ry)
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        margin = do - ds  # positive means we are closer
        cand = (margin, ds, rx, ry)
        if best is None or (margin > best[0]) or (margin == best[0] and ds < best[1]):
            best = cand
        if best_fallback is None or ds < best_fallback[0]:
            best_fallback = (ds, rx, ry)

    if best is not None and best[0] > 0:
        tx, ty = best[2], best[3]
    elif best_fallback is not None:
        tx, ty = best_fallback[1], best_fallback[2]
    else:
        tx, ty = w // 2, h // 2

    # Evaluate moves: approach target; also keep pressure by staying closer to opponent
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not valid(nx, ny):
            continue
        dist_target = md(nx, ny, tx, ty)
        dist_to_opp = md(nx, ny, ox, oy)
        score = dist_target + 0.2 * dist_to_opp  # minimize
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]