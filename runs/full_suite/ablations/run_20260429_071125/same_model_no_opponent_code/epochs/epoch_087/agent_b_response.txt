def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Target: prioritize resources where we are closer than opponent; otherwise contest the best gap.
    best_t = resources[0]
    best_v = -10**9
    for x, y in resources:
        myd = cheb(sx, sy, x, y)
        opd = cheb(ox, oy, x, y)
        # Strongly prefer being ahead; if behind, still prefer smallest loss.
        v = (opd - myd) * 10 - myd
        if v > best_v:
            best_v = v
            best_t = (x, y)

    tx, ty = best_t
    myd0 = cheb(sx, sy, tx, ty)
    opd0 = cheb(ox, oy, tx, ty)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        # If moving closer, improve; also try to be less vulnerable by increasing opponent distance.
        score = 0
        if myd < myd0:
            score += 30
        elif myd == myd0:
            score += 10
        else:
            score -= 25 * (myd - myd0)
        opd = opd0  # opponent not moved this turn; use current to bias toward contesting
        score += (opd - myd) * 8
        # Small tie-break: prefer not leaving immediate capture square if multiple equal.
        if myd == 0:
            score += 1000
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]