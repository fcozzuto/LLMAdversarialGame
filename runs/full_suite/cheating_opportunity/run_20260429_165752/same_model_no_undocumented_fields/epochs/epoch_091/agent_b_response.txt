def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ti = int(observation.get("turn_index") or 0)
    if ti & 1:
        moves = [moves[i] for i in range(4, 9)] + [moves[i] for i in range(4)]

    if not resources:
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -(cheb(nx, ny, ox, oy))
            if v > best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    opp_dists = []
    for rx, ry in resources:
        opp_dists.append(cheb(ox, oy, rx, ry))
    opp_best = min(opp_dists) if opp_dists else 99

    best_val = -10**18
    best_move = (0, 0)

    # Deterministic resource ordering helps tie-breaking
    resources_sorted = sorted(resources, key=lambda p: (p[0], p[1]))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        self_best = 99
        lead_sum = 0
        chosen = None
        for rx, ry in resources_sorted:
            d = cheb(nx, ny, rx, ry)
            if d < self_best:
                self_best = d
                chosen = (rx, ry)
        # Favor moves that make us closer than the opponent to at least one resource
        # Value combines: being closer, creating lead over opponent, and preferring nearer leads.
        for i, (rx, ry) in enumerate(resources_sorted):
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if od - sd > 0:
                lead_sum += (od - sd) * 10 - sd
            elif sd < self_best + 1:
                lead_sum -= sd * 0.5
        # Encourage reducing opponent's best competition indirectly
        self_gain = (opp_best - self_best)
        val = self_gain * 100 + lead_sum
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]