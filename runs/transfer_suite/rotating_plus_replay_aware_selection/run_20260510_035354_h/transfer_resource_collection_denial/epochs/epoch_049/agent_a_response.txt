def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
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

    ox, oy = observation.get("opponent_position", [0, 0])

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If immediate pickup exists, take the first deterministic one.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny) and (nx, ny) in res:
            return [dx, dy]

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_d = cheb(nx, ny, ox, oy)  # how close we are to opponent (lower is bad)
        # Choose target resource that maximizes "we are closer than opponent" advantage.
        # Key: (advantage, -my_steps_to_resource, my_d) with lexicographic ordering.
        best_key = None
        for rx, ry in res:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_self
            key = (adv, -d_self, my_d)
            if best_key is None or key > best_key:
                best_key = key

        # Prefer larger advantage and quicker pickup. Penalize proximity to opponent.
        key2 = best_key
        if best is None or key2 > best:
            best = key2
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]