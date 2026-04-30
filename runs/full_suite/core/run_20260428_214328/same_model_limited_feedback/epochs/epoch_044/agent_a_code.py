def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obst:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            ds = abs(nx - ox) + abs(ny - oy)
            d_self = abs(nx - sx) + abs(ny - sy)
            v = (ds, -d_self, -dx, -dy)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_r = None
        best_r_score = None
        for rx, ry in resources:
            ds = abs(nx - rx) + abs(ny - ry)
            do = abs(ox - rx) + abs(oy - ry)
            score = (do - ds, -ds, -rx, -ry)
            if best_r_score is None or score > best_r_score:
                best_r_score = score
                best_r = (rx, ry)
        v = (best_r_score, -abs(nx - ox) - abs(ny - oy), -dx, -dy)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]