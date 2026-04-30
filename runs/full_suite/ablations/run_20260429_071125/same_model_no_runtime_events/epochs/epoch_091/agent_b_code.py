def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not inb(sx, sy):
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_cell(x, y):
        if not inb(x, y):
            return -10**9
        if resources:
            best = -10**9
            for rx, ry in resources:
                dS = cheb(x, y, rx, ry)
                dO = cheb(ox, oy, rx, ry)
                best = max(best, (dO - dS) * 10 - dS)
            return best
        # No resources: drift away from opponent while staying somewhat central.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dAway = cheb(x, y, ox, oy)
        dCenter = abs(x - cx) + abs(y - cy)
        return dAway * 2 - dCenter

    best_move = [0, 0]
    best_score = score_cell(sx, sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = score_cell(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]
    return best_move