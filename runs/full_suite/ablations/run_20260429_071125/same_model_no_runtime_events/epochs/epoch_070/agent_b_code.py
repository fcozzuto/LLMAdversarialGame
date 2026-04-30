def choose_move(observation):
    w = int(observation.get("grid_width") or 8) or 8
    h = int(observation.get("grid_height") or 8) or 8
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

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
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obst_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    def opp_pressure(x, y):
        d = cheb(x, y, ox, oy)
        return 0 if d > 2 else (4 - d) * 0.7

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        min_after = None
        min_before = None
        for rx, ry in resources:
            a = cheb(nx, ny, rx, ry)
            b = cheb(sx, sy, rx, ry)
            if min_after is None or a < min_after:
                min_after = a
            if min_before is None or b < min_before:
                min_before = b
        # Prefer moves that reduce distance to the closest reachable resource
        progress = (min_before - min_after) if min_before is not None else 0

        # If opponent can reach that closest resource about as fast, slightly avoid those targets
        closest = None
        closest_d = None
        for rx, ry in resources:
            a = cheb(nx, ny, rx, ry)
            if closest_d is None or a < closest_d:
                closest_d = a
                closest = (rx, ry)
        opp_fast = 0
        if closest is not None:
            rx, ry = closest
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if opd <= myd:
                opp_fast = (myd - opd + 1) * 0.9

        score = (-progress) + obst_pen(nx, ny) * 0.8 + opp_pressure(nx, ny) + opp_fast * 0.6
        if best is None or score < best or (score == best and (dx, dy) < best_move):
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]