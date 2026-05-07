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

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    resources2 = [(r[0], r[1]) for r in resources if r and len(r) >= 2]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = (0, 0)
    best_val = -10**18

    # Deterministic ordering of resources to break ties
    resources2.sort()

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not free(nx, ny):
            continue

        immediate = 0
        for rx, ry in resources2:
            if nx == rx and ny == ry:
                immediate = 1
                break

        # Resource-denial objective: maximize how much closer we are than opponent.
        # Value = big immediate + best advantage, penalized by remaining distance.
        best_adv = -10**18
        best_dist = 10**18
        for rx, ry in resources2:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - our_d  # positive means we can out-reach opponent
            # Prefer larger advantage; if equal, prefer smaller our distance
            if adv > best_adv or (adv == best_adv and our_d < best_dist):
                best_adv = adv
                best_dist = our_d

        val = immediate * 10**6 + best_adv * 1000 - best_dist
        if val > best_val:
            best_val = val
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]