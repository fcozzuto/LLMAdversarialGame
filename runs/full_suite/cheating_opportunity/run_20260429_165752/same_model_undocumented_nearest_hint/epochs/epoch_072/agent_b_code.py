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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    if resources:
        best_t = None
        best_sc = -10**18
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Materially different from previous: explicit "gain over opponent" target
            sc = (d_opp - d_me) * 1000 - d_me - cheb(rx, ry, W//2, H//2)
            if sc > best_sc:
                best_sc = sc
                best_t = (rx, ry)

        tx, ty = best_t
        # 1-step lookahead on all legal moves toward the chosen advantage target
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d_me2 = cheb(nx, ny, tx, ty)
            d_opp2 = cheb(ox, oy, tx, ty)
            val = (d_opp2 - d_me2) * 1000 - d_me2
            # Slightly discourage moving into immediate contact with opponent
            if cheb(nx, ny, ox, oy) <= 1:
                val -= 50
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources left: deterministically move to maximize distance from opponent
    best_move = (0, 0)
    best_d = -1
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        if d > best_d:
            best_d = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]