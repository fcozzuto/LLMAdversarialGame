def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        targets = []
        for r in resources:
            try:
                rx, ry = r
            except:
                continue
            rx, ry = int(rx), int(ry)
            if inb(rx, ry) and (rx, ry) not in obs:
                targets.append((rx, ry))
        if targets:
            best_move = (0, 0)
            best_score = None
            tx0, ty0 = w // 2, h // 2
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not free(nx, ny):
                    continue
                my_to = min(dist(nx, ny, rx, ry) for rx, ry in targets)
                opp_to = min(dist(ox, oy, rx, ry) for rx, ry in targets)
                score = (my_to - opp_to, dist(nx, ny, tx0, ty0) + dist(nx, ny, ox, oy))
                if best_score is None or score < best_score:
                    best_score = score
                    best_move = (dx, dy)
            return [best_move[0], best_move[1]]

    cx, cy = w // 2, h // 2
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        score = (-dist(nx, ny, ox, oy), dist(nx, ny, cx, cy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]