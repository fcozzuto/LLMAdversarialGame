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

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def pick_target():
        if not resources:
            return ((W - 1) // 2, (H - 1) // 2)
        best_t = resources[0]
        best_val = -10**9
        for rx, ry in resources:
            dS = cheb(sx, sy, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            rel = (rx + ry) - (ox + oy)  # prefer farther from opponent diagonal bias
            val = (dO - dS) * 1000 - dS * 10 + rel * 0.5
            if val > best_val:
                best_val = val
                best_t = (rx, ry)
        return best_t

    tx, ty = pick_target()

    best_move = (0, 0)
    best_eval = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dT = cheb(nx, ny, tx, ty)
        dO = cheb(nx, ny, ox, oy)
        val = -dT * 1000 + dO * 5
        if (nx, ny) == (tx, ty):
            val += 10**7
        if val > best_eval:
            best_eval = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]