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

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_sc = -10**18

    if resources:
        # deterministic: break ties by preferring earlier move in list
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d_r = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            d_o = cheb(nx, ny, ox, oy)
            sc = (-d_r * 10) + d_o
            if best is None or sc > best_sc:
                best_sc = sc
                best = [dx, dy]
    else:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d_o = cheb(nx, ny, ox, oy)
            sc = d_o
            if best is None or sc > best_sc:
                best_sc = sc
                best = [dx, dy]

    if best is not None:
        return [int(best[0]), int(best[1])]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]