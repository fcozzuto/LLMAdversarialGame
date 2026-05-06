def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def edge_cost(x, y):
        d = x
        if w - 1 - x < d:
            d = w - 1 - x
        if y < d:
            d = y
        if h - 1 - y < d:
            d = h - 1 - y
        return d

    ox, oy = observation["opponent_position"]
    valid_resources = [tuple(r) for r in resources if tuple(r) not in obstacles]
    if not valid_resources:
        return [0, 0]

    # Predict opponent greedy-next-step toward nearest resource (deterministic tie-break)
    opp_best = (ox, oy)
    best_d = None
    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = min(cheb(nx, ny, rx, ry) for rx, ry in valid_resources)
        if best_d is None or nd < best_d:
            best_d = nd
            opp_best = (nx, ny)
    opnx, opny = opp_best

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        for rx, ry in valid_resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(opnx, opny, rx, ry)
            adv = od - md
            if md == 0:
                adv += 2.5
            if od == 0 and md != 0:
                adv -= 2.5
            score += adv
        score -= 0.02 * edge_cost(nx, ny)
        key = (score, -cheb(nx, ny, sx, sy), -dx, -dy)  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]