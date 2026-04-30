def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_dx, best_dy = 0, 0
    best_val = -10**18

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            my_b = 10**9
            opp_b = 10**9
            adv = -10**18
            for rx, ry in resources:
                myd = dist(nx, ny, rx, ry)
                opd = dist(ox, oy, rx, ry)
                if myd < my_b:
                    my_b = myd
                if opd < opp_b:
                    opp_b = opd
                a = opd - myd
                if a > adv:
                    adv = a
            val = 1000 * adv - my_b
            if val > best_val or (val == best_val and (dx, dy) < (best_dx, best_dy)):
                best_val = val
                best_dx, best_dy = dx, dy
    else:
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            val = dist(nx, ny, ox, oy)
            if val > best_val or (val == best_val and (dx, dy) < (best_dx, best_dy)):
                best_val = val
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]