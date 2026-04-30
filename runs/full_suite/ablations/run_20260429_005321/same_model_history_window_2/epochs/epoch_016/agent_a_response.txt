def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
            res.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_adj_pen(x, y):
        pen = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obst:
                pen += 1
        return pen

    if not res:
        best = (-(10**18), 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            score = -obst_adj_pen(nx, ny) - cheb(nx, ny, ox, oy)
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    best_score = -(10**18)
    best_dx, best_dy = 0, 0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        d_self_closest = min(cheb(nx, ny, rx, ry) for rx, ry in res)
        # Lead over opponent on some target is prioritized.
        lead = -10**18
        for rx, ry in res:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # prefer moves that get strictly closer than opponent can.
            v = d_opp - d_self
            if v > lead:
                lead = v

        # Encourage approaching while penalizing near-obstacle congestion.
        score = (lead * 1000) - d_self_closest - obst_adj_pen(nx, ny) * 2
        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]