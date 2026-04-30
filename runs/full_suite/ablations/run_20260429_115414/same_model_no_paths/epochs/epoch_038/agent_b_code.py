def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    s = observation.get("self_position", [0, 0])
    o = observation.get("opponent_position", [0, 0])
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # fallback: step to increase distance from opponent while staying legal
        best_move = (0, 0)
        best = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy)
            if v > best:
                best, best_move = v, (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose best target: prefer resources where we are relatively closer to gain tempo.
    # Also prefer stealing: if opponent is close, pick a resource where we can still out-race them.
    best_t = None
    best_key = None
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - md  # positive means we are closer
        # Slightly prefer closer overall when adv similar, deterministically.
        key = (adv, -md, -rx, -ry)
        if best_key is None or key > best_key:
            best_key, best_t = key, (rx, ry)
    tx, ty = best_t

    # Evaluate one-step moves against that target and lightly against opponent.
    # This is a materially different behavior than pure "move to nearest resource": it
    # also considers relative race pressure on the opponent for the selected target.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Main: reduce my distance; Secondary: increase opponent's relative lag.
        # Tertiary: slightly push away from opponent to reduce contest interference.
        score = (-myd) + (opd - myd) * 0.35 + cheb(nx, ny, ox, oy) * 0.05
        # Deterministic tie-break: prefer diagonal/orthogonal order by fixed (dx,dy) scanning.
        if score > best_score:
            best_score, best_move = score, (dx, dy)

    return [best_move[0], best_move[1]]