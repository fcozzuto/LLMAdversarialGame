def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # If no resources, move toward center or stay
    if not resources:
        cx, cy = w // 2, h // 2
        tx = max(0, min(w - 1, cx))
        ty = max(0, min(h - 1, cy))
        dx = 0
        dy = 0
        if sx < tx: dx = 1
        elif sx > tx: dx = -1
        if sy < ty: dy = 1
        elif sy > ty: dy = -1
        if not legal(sx + dx, sy + dy):
            dx, dy = 0, 0
        return [dx, dy]

    # Decide on a target resource deterministically: closest to us, breaking ties by being farther from opponent
    best_r = None
    best_d = None
    best_od = None
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        if best_r is None or d < best_d or (d == best_d and od > best_od):
            best_r = (rx, ry)
            best_d = d
            best_od = od

    tx, ty = best_r

    # Move towards target with simple step, avoid obstacles
    dx = 0
    dy = 0
    if sx < tx: dx = 1
    elif sx > tx: dx = -1
    if sy < ty: dy = 1
    elif sy > ty: dy = -1

    # Validate move; if blocked, try to adjust
    cand = [(dx, dy), (dx, 0), (0, dy), (0,0), (-dx, -dy)]
    for ax, ay in cand:
        nx, ny = sx + ax, sy + ay
        if (ax, ay) == (0,0):
            nx, ny = sx, sy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [ax, ay]

    # Fallback: try some neighboring free cell
    for ax in (-1,0,1):
        for ay in (-1,0,1):
            nx, ny = sx + ax, sy + ay
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [ax, ay]

    return [0,0]