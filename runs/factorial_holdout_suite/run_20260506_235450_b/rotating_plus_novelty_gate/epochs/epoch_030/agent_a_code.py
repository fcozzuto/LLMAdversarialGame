def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_adv(px, py):
        best = None
        for rx, ry in resources:
            sd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            key = (adv, -sd, abs(ry - oy), -((rx + ry) & 1))
            if best is None or key > best[0]:
                best = (key, sd)
        return best[0][0], best[0][1]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        adv, sd = best_adv(nx, ny)
        # Prefer moves that can secure a nearby resource, and avoid giving opponent a big advantage.
        od_near = min(cheb(ox, oy, rx, ry) for rx, ry in resources)
        key = (adv, -sd, -od_near, dx == 0 and dy == 0, -((nx + ny) & 1))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move if inb(sx + best_move[0], sy + best_move[1]) else [0, 0]