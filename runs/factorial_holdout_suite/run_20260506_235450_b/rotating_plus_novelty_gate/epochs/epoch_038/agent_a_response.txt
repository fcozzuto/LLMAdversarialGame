def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_score = -10**18
    best_move = (0, 0)

    # small deterministic tie-breaker: prefer lower dx, then lower dy
    def tiebreak(dx, dy):
        return (dx, dy)

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not free(nx, ny):
            continue

        on_resource = 0
        best_adv = -10**18
        best_self_dist = 10**9

        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            if nx == rx and ny == ry:
                on_resource = 1
                best_adv = 10**6
                best_self_dist = 0
                break
            adv = d_opp - d_self  # want to be closer than opponent
            if adv > best_adv or (adv == best_adv and d_self < best_self_dist):
                best_adv = adv
                best_self_dist = d_self

        # Favor immediate collection, then resource advantage; slight bias toward minimizing own distance
        score = on_resource * 10**7 + best_adv * 1000 - best_self_dist

        if score > best_score or (score == best_score and tiebreak(dxm, dym) < tiebreak(best_move[0], best_move[1])):
            best_score = score
            best_move = (dxm, dym)

    return [best_move[0], best_move[1]]