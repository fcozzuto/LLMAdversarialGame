def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            nx = x + dx
            if nx < 0 or nx >= w: 
                continue
            for dy in (-1, 0, 1):
                ny = y + dy
                if 0 <= ny < h and (nx, ny) in obstacles:
                    if not (nx == x and ny == y):
                        c += 1
        return c

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = (od - sd) * 20 - sd - 2 * near_obst(rx, ry)
        if best is None or val > best[0] or (val == best[0] and sd < best[1]):
            best = (val, sd, rx, ry)
    _, _, tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = cheb(nx, ny, tx, ty)
            # small bias to avoid moving into tighter obstacle neighborhoods
            pen = near_obst(nx, ny)
            # if opponent is adjacent to the target, prefer closer approach this turn
            opp_pen = 0
            if cheb(ox, oy, tx, ty) <= 1 and (d == 0 or d == 1):
                opp_pen = -2
            score = (d, pen + 0.5, -opp_pen)
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]
    return best_move