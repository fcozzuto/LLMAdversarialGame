def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = (W - 1) // 2, (H - 1) // 2

    best_r = None
    best_score = -10**9
    for rx, ry in resources:
        md = dist_cheb(sx, sy, rx, ry)
        od = dist_cheb(ox, oy, rx, ry)
        # prefer resources we can reach earlier; mild preference for being closer
        score = (od - md) * 100 - md
        # deterministic tie-break: prefer smaller md then smaller lex
        if score > best_score:
            best_score = score
            best_r = (rx, ry)
        elif score == best_score and best_r is not None:
            bdx = dist_cheb(sx, sy, best_r[0], best_r[1])
            if md < bdx or (md == bdx and (rx, ry) < best_r):
                best_r = (rx, ry)

    if best_r is None:
        tx, ty = cx, cy
    else:
        tx, ty = best_r

    # Choose a move that reduces distance to target; tie-break to minimize opponent distance.
    best_move = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        nd = dist_cheb(nx, ny, tx, ty)
        od = dist_cheb(nx, ny, ox, oy)
        val = (nd, od, dx, dy)  # lexicographic deterministic
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]