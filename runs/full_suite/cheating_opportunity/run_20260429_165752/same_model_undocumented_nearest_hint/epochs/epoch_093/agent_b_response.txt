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
    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    def score_pos(px, py):
        if not resources:
            # Late game: drift toward center, but keep moving away from worst corner when possible
            dc = abs(px - cx) + abs(py - cy)
            do = cheb(px, py, ox, oy)
            return (-dc, -do)
        best = None
        # Maximize (opponent_distance - my_distance); tie-break by smaller my_distance, then closeness to center
        for rx, ry in resources:
            myd = cheb(px, py, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            # discourage targets I can't plausibly beat
            if myd > opd + 1:
                adv -= 1000
            t = (adv, -myd, -((abs(px - cx) + abs(py - cy))))
            if best is None or t > best:
                best = t
        return best

    best_move = (0, 0)
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        sc = score_pos(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]