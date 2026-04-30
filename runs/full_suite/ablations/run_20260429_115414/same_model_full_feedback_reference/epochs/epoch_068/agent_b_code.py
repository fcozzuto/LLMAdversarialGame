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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    legal = [(dx, dy) for dx, dy in moves if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    if resources:
        best = None
        best_key = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # target resource where we are relatively closer than opponent
            best_res_key = None
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # prefer resources we can reach earlier; slight penalty for being far
                key = (myd - opd, myd, opd, rx, ry)
                if best_res_key is None or key < best_res_key:
                    best_res_key = key
            # prefer moves that improve the chosen target
            myd0 = best_res_key[1]
            move_key = (best_res_key[0], best_res_key[2], myd0, abs((nx - ox)) + abs((ny - oy)), dx, dy)
            if best_key is None or move_key < best_key:
                best_key = move_key
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # No visible resources: go to center while increasing distance from opponent
    cx, cy = (W - 1) // 2, (H - 1) // 2
    best = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        key = (cheb(nx, ny, cx, cy), -cheb(nx, ny, ox, oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]