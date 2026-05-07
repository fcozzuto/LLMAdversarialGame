def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b, c, d):
        ddx = a - c
        if ddx < 0: ddx = -ddx
        ddy = b - d
        if ddy < 0: ddy = -ddy
        return ddx + ddy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    # Pick resource where we are closer; otherwise reduce the gap most.
    best = None
    best_score = -10**18
    for rx, ry in resources:
        md = man(rx, ry, sx, sy)
        od = man(rx, ry, ox, oy)
        # Strongly prefer states where we can arrive first; otherwise minimize our delay vs opponent.
        score = (od - md) * 100 - md
        # Slightly favor central-ish routes to reduce being stuck by obstacles.
        score += -abs(rx - (w - 1) / 2) * 0.5 - abs(ry - (h - 1) / 2) * 0.5
        if score > best_score:
            best_score = score
            best = (rx, ry)

    rx, ry = best

    # One-step lookahead: choose legal move minimizing our distance and maximizing advantage over opponent.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if not inb(nx, ny):
            continue
        myd = man(rx, ry, nx, ny)
        opd = man(rx, ry, ox, oy)
        val = (opd - myd) * 100 - myd
        # If we can step closer, prefer it; also avoid moves that increase distance to our target.
        val += - (0 if myd <= man(rx, ry, sx, sy) else 20)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]