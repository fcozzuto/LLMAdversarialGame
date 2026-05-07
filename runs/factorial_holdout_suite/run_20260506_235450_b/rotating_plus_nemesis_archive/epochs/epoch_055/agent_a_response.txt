def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if resources:
        best_r = None
        best_key = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            key = (od - sd, -sd, -rx, -ry)  # want to be closer than opponent
            if best_key is None or key > best_key:
                best_key, best_r = key, (rx, ry)
        tx, ty = best_r
    else:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # if no visible resources, drift toward a corner farthest from opponent
        tx, ty = max(corners, key=lambda c: man(c[0], c[1], ox, oy))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        # primary: reach target sooner; secondary: deny opponent by keeping (od2 - sd2) high
        score = (od2 - sd2, -sd2, -nx, -ny)
        if best_score is None or score > best_score:
            best_score, best = score, (dx, dy)
    return [int(best[0]), int(best[1])]