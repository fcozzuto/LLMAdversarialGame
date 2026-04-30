def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obstacle_penalty(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick the resource we can beat first; if none, pick closest to deny.
    target = None
    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer positive lead; add slight tie-break by absolute closeness.
        lead = opd - myd
        utility = (lead * 10) - myd - 0.05 * (rx * 3 + ry * 7)
        # If lead is non-positive, still allow but with a big penalty (deny/contend).
        if lead <= 0:
            utility -= 20
        if best is None or utility > best or (utility == best and (rx, ry) < target):
            best = utility
            target = (rx, ry)

    if target is None:
        # No visible resources: drift to opponent side while avoiding obstacles.
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
    else:
        tx, ty = target

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Avoid moves that give opponent a strong immediate advantage.
        oppd = cheb(ox, oy, tx, ty)
        myd_curr = cheb(sx, sy, tx, ty)
        # predicted advantage term encourages maintaining/creating lead
        adv = (oppd - nd)
        score = (adv * 8) - nd - obstacle_penalty(nx, ny) - (0.01 * (nx * 5 + ny * 11))
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]