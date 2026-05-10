def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            neigh.append((nx, ny, dx, dy))
    if not neigh:
        return [0, 0]

    valid_res = []
    for p in resources:
        rx, ry = p[0], p[1]
        if inb(rx, ry) and (rx, ry) not in obstacles:
            valid_res.append((rx, ry))
    if not valid_res:
        return [0, 0]

    best = None
    for nx, ny, dx, dy in neigh:
        best_val = None
        for rx, ry in valid_res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            key = (-adv, sd, od, rx, ry)  # prioritize gaining over opponent
            if best_val is None or key < best_val:
                best_val = key
        # small tiebreaker: prefer moving closer overall
        settle = (best_val, abs(nx - sx) + abs(ny - sy))
        if best is None or settle < best[0]:
            best = (settle, (dx, dy))

    return [best[1][0], best[1][1]]