def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)  # Chebyshev

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp = (ox, oy)

    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestv = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = dist((nx, ny), (tx, ty)) - 0.08 * dist((nx, ny), opp)
            if v < bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Intercept: estimate opponent's nearest target, then move to reduce (our_dist - opp_dist).
    target = None
    best_t = 10**18
    for r in resources:
        d = dist((ox, oy), r)
        if d < best_t or (d == best_t and (r[0] + r[1] < target[0] + target[1] if target else False)):
            best_t = d
            target = tuple(r)

    tx, ty = target
    opp_to_t = dist(opp, (tx, ty))

    # Tie-breaks: avoid getting stuck near obstacles and keep some distance from opponent if possible.
    best = [0, 0]
    bestv = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_to_t = dist((nx, ny), (tx, ty))
        my_vs_opp = my_to_t - opp_to_t  # lower is better (faster intercept)
        my_to_opp = dist((nx, ny), opp)

        # Small preference for moving toward any resource if intercept scores tie.
        best_any = 10**18
        for r in resources:
            d = dist((nx, ny), r)
            if d < best_any:
                best_any = d

        # Penalize stepping next to obstacles too often (local trap avoidance)
        adj_block = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    adj_block += 1

        v = my_vs_opp * 10 + my_to_t + (-0.02 * my_to_opp) + (0.35 * adj_block) + (0.01 * best_any)
        if v < bestv:
            bestv = v
            best = [dx, dy]
    return best