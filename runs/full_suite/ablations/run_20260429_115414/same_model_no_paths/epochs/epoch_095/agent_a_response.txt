def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    my_to = {}
    for rx, ry in resources:
        my_to[(rx, ry)] = cheb(sx, sy, rx, ry)

    best = None
    best_score = None
    for rx, ry in resources:
        ds = my_to[(rx, ry)]
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach no later; otherwise prefer those where we're closer.
        # Deterministic tie-break by (rx,ry).
        score = (do - ds) * 1000 - ds * 3 + (rx * 0 + ry)  # ry used only as deterministic small offset
        if best is None or score > best_score or (score == best_score and (rx, ry) < best):
            best = (rx, ry)
            best_score = score

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Prefer moves that reduce distance most; then closer to target while maintaining advantage vs opponent.
        opp_d = cheb(ox, oy, tx, ty)
        cand_score = (opp_d - d) * 1000 - d
        candidates.append((cand_score, d, nx, ny, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True, key=lambda t: (t[0], -t[1], -t[2], -t[3], -t[4], -t[5]))
    return [int(candidates[0][4]), int(candidates[0][5])]