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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obstacle_pen(x, y):
        p = 0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            if (x + dx, y + dy) in obstacles:
                p += 1
        return -p

    def opp_risk_pen(x, y):
        d = cheb(x, y, ox, oy)
        if d == 0:
            return -100
        return - (6 if d == 1 else 2 if d == 2 else 0)

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        score = 0
        score += near_obstacle_pen(nx, ny)
        score += opp_risk_pen(nx, ny)

        if resources:
            best_adv = -10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Prefer resources where we are closer than the opponent, scaled by distance advantage.
                adv = (opd - myd)
                # Slightly prefer moves that also reduce absolute distance to high-value pickups.
                adv -= (myd * 0.15)
                if (rx, ry) == (nx, ny):
                    adv += 50
                if adv > best_adv:
                    best_adv = adv
            score += best_adv
        else:
            # If no resources known, drift deterministically toward opponent's corner opposite: maximize distance.
            score += cheb(nx, ny, ox, oy) * 0.1

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]