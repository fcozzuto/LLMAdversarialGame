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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best_target = resources[0]
    best_val = -10**9
    for rx, ry in resources:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; small penalty for far distance.
        val = (d_opp - d_self) * 100 - d_self
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target
    cur_d = cheb(sx, sy, tx, ty)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, nx, ny)
        # Primary: get closer to target; Secondary: avoid stepping near opponent.
        score = (cur_d - d_self) * 1000 - d_self * 5 + d_opp * 0.5
        # Avoid oscillations into dead zones: favor moves that reduce distance to target.
        if dx == 0 and dy == 0:
            score -= 3
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]