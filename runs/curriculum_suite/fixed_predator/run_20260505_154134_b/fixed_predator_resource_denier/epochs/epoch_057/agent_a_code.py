def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles if p and len(p) >= 2}

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)]
    best_move, best_score = (0, 0), -10**9

    # Pick target resource: prefer those we can reach not later than opponent; tie-break by best advantage.
    target = None
    best_adv = -10**9
    best_dist = 10**9
    for r in resources:
        if not r or len(r) < 2: 
            continue
        rx, ry = r[0], r[1]
        if (rx, ry) in obs or not inb(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if sd <= od:
            if adv > best_adv or (adv == best_adv and sd < best_dist):
                best_adv, best_dist, target = adv, sd, (rx, ry)

    # If no escapable target, just reduce opponent pressure: head toward opponent.
    if target is None:
        tx, ty = ox, oy
    else:
        tx, ty = target

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # Primary: get closer to chosen target; secondary: deny opponent by reducing its advantage.
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        score = (-sd) + (od - cheb(nx, ny, tx, ty)) * 0.1
        # Small bias to keep moving (avoid staying unless needed)
        if dx == 0 and dy == 0: score -= 0.05
        if score > best_score:
            best_score, best_move = score, [dx, dy]

    return [int(best_move[0]), int(best_move[1])]