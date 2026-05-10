def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    for p in resources:
        if p and len(p) >= 2:
            res.append((p[0], p[1]))
    if not res:
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

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_center = -(((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) / (w * h))
        best_res_val = -10**18
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Favor resources where we are closer than opponent; penalize absolute delay.
            v = (opd - myd) * 4.0 - myd + my_center * 0.6
            # If tie or near tie, prefer closer-in resources deterministically.
            v -= (myd == 0) * 0.0
            if v > best_res_val:
                best_res_val = v
        # Small bias to avoid staying if another move is equally good.
        if best_res_val > best_val or (best_res_val == best_val and (dx, dy) != (0, 0)):
            best_val = best_res_val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]