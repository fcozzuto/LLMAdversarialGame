def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # fallback: move toward center deterministically
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            s = cheb(nx, ny, cx, cy)
            if (s, dx, dy) < best:
                best = (s, dx, dy)
        dx, dy = best[1], best[2]
        return [dx, dy] if inb(sx + dx, sy + dy) else [0, 0]

    # Precompute opponent nearest distances to each resource
    opp_best = {}
    for rx, ry in resources:
        opp_best[(rx, ry)] = cheb(ox, oy, rx, ry)

    # Choose move maximizing (opponent advantage we can steal) and breaking ties by progress/center bias
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        our_min_d = 10**9
        steal_score = -10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            our_min_d = d if d < our_min_d else our_min_d
            # if we can reach earlier than opponent: positive; otherwise less
            adv = opp_best[(rx, ry)] - d
            if adv > steal_score:
                steal_score = adv
        # Encourage strong stealing, and slightly prefer closer to center and closer to some resource
        val = steal_score * 1000 + (-our_min_d) * 3 - cheb(nx, ny, cx, cy)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]