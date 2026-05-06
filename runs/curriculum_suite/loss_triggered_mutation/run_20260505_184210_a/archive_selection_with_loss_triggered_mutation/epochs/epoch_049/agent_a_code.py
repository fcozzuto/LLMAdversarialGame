def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick a target resource where we are currently best positioned vs the denier
    best_res = None
    best_margin = -10**18
    best_dist = 10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd  # positive means we are closer than opponent
        if margin > best_margin or (margin == best_margin and (sd < best_dist or (sd == best_dist and (rx + ry) < (best_res[0] + best_res[1])))):
            best_margin = margin
            best_dist = sd
            best_res = (rx, ry)

    tx, ty = best_res
    cur_to_t = cheb(sx, sy, tx, ty)
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy, nx, ny in valid:
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)  # approximate next-turn opponent access
        # Prefer moves that reduce our distance and increase our lead; also avoid giving opponent advantage.
        score = (opd - myd) * 10 - myd
        if myd < cur_to_t:
            score += 3
        if (nx, ny) == (tx, ty):
            score += 60
        # Slightly bias away from direct collision with opponent to reduce denial attempts
        if cheb(nx, ny, ox, oy) <= 1:
            score -= 2
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]