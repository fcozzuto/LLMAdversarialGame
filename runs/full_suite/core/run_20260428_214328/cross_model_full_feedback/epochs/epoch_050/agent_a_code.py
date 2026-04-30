def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y):
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inside(x, y) and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    tx, ty = ox, oy
    if resources:
        best = None
        bestd = 10**9
        for (rx, ry) in resources:
            d = cheb(sx, sy, rx, ry)
            if d < bestd:
                bestd = d; best = (rx, ry)
            elif d == bestd and best is not None and (rx, ry) < best:
                best = (rx, ry)
        tx, ty = best

    best_move = moves[0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        d_to = cheb(nx, ny, tx, ty)
        score = -d_to
        if resources and (nx, ny) in resources:
            score += 1000
        d_opp = cheb(nx, ny, ox, oy)
        score += 0 if resources else -d_opp * 0.2
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
        elif score == best_score and [dx, dy] < best_move:
            best_move = [dx, dy]
    return best_move