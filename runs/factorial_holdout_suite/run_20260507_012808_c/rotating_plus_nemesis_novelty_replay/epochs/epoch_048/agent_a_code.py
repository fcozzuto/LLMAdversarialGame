def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    opp_target_x = (w - 1) if (oy % 2 == 0) else 0
    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx > 0 else -dx if dx < 0 else 0

    def dist(x1, y1, x2, y2):
        adx = x1 - x2
        if adx < 0: adx = -adx
        ady = y1 - y2
        if ady < 0: ady = -ady
        return adx if adx > ady else ady

    best = (10**9, 0, 0)
    moves = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    if not moves:
        return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            md = min(dist(nx, ny, rx, ry) for rx, ry in resources)
            tx_pen = 0
            if nx == opp_target_x:
                tx_pen = 4
            score = md + tx_pen
        else:
            score = dist(nx, ny, ox, oy)  # go closer when no resources
        if score < best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]