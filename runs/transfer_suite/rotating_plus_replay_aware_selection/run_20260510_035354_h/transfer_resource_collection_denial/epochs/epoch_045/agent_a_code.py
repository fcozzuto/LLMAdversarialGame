def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obs:
                res.add((x, y))
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best_key = None
    best = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Immediate pickup if we land on a resource
        if (nx, ny) in res:
            key = (10**9, 0, 0, 0)
            best_key = key
            best = [dx, dy]
            break

        my_pos_d = []
        # Choose the resource that maximizes how much sooner we can arrive than opponent
        best_adv = -10**18
        best_my_d = 10**9
        best_opp_d = 10**9
        for rx, ry in res:
            my_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - my_d
            if adv > best_adv or (adv == best_adv and my_d < best_my_d) or (adv == best_adv and my_d == best_my_d and opp_d < best_opp_d):
                best_adv, best_my_d, best_opp_d = adv, my_d, opp_d

        # Tie-break: more advantage, then closer to target, then further from opponent to reduce contest
        key = (best_adv, -best_my_d, best_opp_d, -abs((nx + ny) - (sx + sy)))
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return [int(best[0]), int(best[1])]