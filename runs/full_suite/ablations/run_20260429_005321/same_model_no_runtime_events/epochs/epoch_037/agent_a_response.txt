def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = (0, 0, 10**9, 10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            ao = cheb(nx, ny, ox, oy)
            cand = (d, -ao, dx, dy)
            if (cand[0], cand[1]) < (best[0], best[1]):
                best = (cand[0], cand[1], cand[2], cand[3])
        return [best[2], best[3]]

    # Find best target considering who is closer
    best_self = None
    best_opp = None
    best_self_d = 10**9
    best_opp_d = 10**9
    for (rx, ry) in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds < best_self_d or (ds == best_self_d and (rx + ry) < sum(best_self or (10**9, 10**9))):
            best_self_d = ds
            best_self = (rx, ry)
        if do < best_opp_d or (do == best_opp_d and (rx + ry) < sum(best_opp or (10**9, 10**9))):
            best_opp_d = do
            best_opp = (rx, ry)

    # If opponent is much closer to its nearest, move to contest it; else go for our nearest.
    # Contest threshold tuned deterministically.
    contest = False
    if best_opp is not None:
        contest = best_self_d > best_opp_d - 1
    tx, ty = (best_opp if contest else best_self)

    # Score candidate moves: primarily reduce distance to target, secondarily increase distance from opponent,
    # and slightly prefer moving along the gradient (toward target) deterministically.
    best_move = (0, 0)
    best_score = (-10**18, 0)  # (score, tie)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_from_opp = cheb(nx, ny, ox, oy)
        # tie-breaker: smaller coordinate sum to be deterministic
        gradient = abs(nx - tx) + abs(ny - ty)
        score = (-d_to_t * 1000) + (d_from_opp * 2) - gradient
        tie = (nx + ny, nx, ny)
        cand = (score, -tie[0])
        if cand > best_score:
            best_score = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]