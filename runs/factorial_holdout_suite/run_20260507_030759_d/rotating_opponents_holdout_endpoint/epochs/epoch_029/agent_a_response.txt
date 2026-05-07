def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        local_best = -10**9
        for tx, ty in res:
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)

            # advantage: larger is better (opp farther than self)
            adv = od - sd

            # small tie-breakers: prefer picking sooner and blocking lines
            # if opponent shares the same Chebyshev line to target, downweight (likely contest)
            same_line = 1 if (nx == ox and tx != nx) or (ny == oy and ty != ny) or (nx - ny == ox - oy) else 0
            penalty = 0.25 * same_line

            score = adv * 10 - sd - penalty

            if score > local_best:
                local_best = score

        if best_score is None or local_best > best_score or (local_best == best_score and (dx, dy) < best_move):
            best_score = local_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]