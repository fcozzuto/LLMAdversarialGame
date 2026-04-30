def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    if resources:
        best_val = -10**9
        best = None
        for rx, ry in resources:
            d_ours = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            val = d_op - d_ours
            if val > best_val or (val == best_val and d_ours < (cheb(sx, sy, best[0], best[1]) if best else 10**9)):
                best_val = val
                best = (rx, ry)
        tx, ty = best
        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d1 = cheb(nx, ny, tx, ty)
            d2 = cheb(nx, ny, ox, oy)
            score = d2 - d1  # prefer approaching our chosen resource while staying farther from opponent
            if score > best_score or (score == best_score and d1 < cheb(sx + best_move[0], sy + best_move[1], tx, ty)):
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: move to maximize distance from opponent while improving toward center
    cx, cy = (W - 1) // 2, (H - 1) // 2
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_center = cheb(nx, ny, cx, cy)
        d_opp = cheb(nx, ny, ox, oy)
        score = d_opp - d_center
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]