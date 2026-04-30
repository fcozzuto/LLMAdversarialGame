def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set()
    for p in obstacles:
        try:
            px, py = int(p[0]), int(p[1])
            obs_set.add((px, py))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs_set

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_r = None
    best_score = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not legal(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Material advantage + race finish preference (lower our distance)
        adv = od - sd
        finish = 100 - sd  # higher when closer
        center_pen = -(((rx - (w // 2)) * (rx - (w // 2))) + ((ry - (h // 2)) * (ry - (h // 2))))
        tie_bonus = 5 if od == sd else 0
        score = (adv * 50) + finish + center_pen + tie_bonus
        if best_score is None or score > best_score or (score == best_score and (rx, ry) < best_r):
            best_score = score
            best_r = (rx, ry)

    if best_r is None:
        # No reachable resources: drift to center while avoiding obstacles deterministically
        tx, ty = w // 2, h // 2
        best = (None, None)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            key = (-d, dx, dy)  # deterministic tiebreak
            if best[0] is None or key > best[0]:
                best = (key, (dx, dy))
        return best[1] if best[1] is not None else [0, 0]

    rx, ry = best_r
    best_move = [0, 0]
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        sd1 = cheb(nx, ny, rx, ry)
        # Prefer moves that increase our advantage and reduce our distance; penalize stepping away
        adv1 = cheb(ox, oy, rx, ry) - sd1
        delta = sd1 - cheb(sx, sy, rx, ry)
        key = (adv1, -sd1, -delta, -(abs(nx - rx) + abs(ny - ry)), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move