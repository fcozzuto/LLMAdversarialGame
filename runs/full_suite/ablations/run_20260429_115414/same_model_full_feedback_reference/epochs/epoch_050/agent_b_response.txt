def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_t = resources[0]
    best_score = -10**9
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # prefer resources we can arrive before opponent; break ties deterministically
        score = (opd - myd) * 100 - myd
        if (opd - myd) >= 0:
            score += 50
        if score > best_score or (score == best_score and (rx, ry) < best_t):
            best_score = score
            best_t = (rx, ry)

    rx, ry = best_t
    myd0 = cheb(sx, sy, rx, ry)
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, rx, ry)
        # if we can't beat opponent, at least try to deny by moving toward the contested resource
        val = (myd0 - myd) * 200 - myd
        # small deterministic "stay-safe": avoid increasing distance to chosen target too much
        if myd <= myd0:
            val += 30
        # further deterministic preference: move with smaller (nx,ny) if equal
        if val > best_val or (val == best_val and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]