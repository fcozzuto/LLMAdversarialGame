def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a; bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = None
    if resources:
        best = None
        bestd = 10**9
        for r in resources:
            d = dist((sx, sy), r)
            if d < bestd:
                bestd = d
                best = r
        target = best
    else:
        target = (ox, oy)

    best_move = (0, 0)
    best_score = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obst:
            continue
        d = dist((nx, ny), target)
        if resources:
            score = d * 1000 + (abs(nx - ox) + abs(ny - oy))
        else:
            score = d
        if score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]