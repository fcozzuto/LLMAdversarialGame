def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_obst(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx or ddy:
                    if (x + ddx, y + ddy) in obstacles:
                        c += 1
        return c

    best_r = None
    best_score = -10**9
    our_d_to = {}
    opp_d_to = {}
    any_fast = False
    for (rx, ry) in resources:
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        our_d_to[(rx, ry)] = our_d
        opp_d_to[(rx, ry)] = opp_d
        diff = opp_d - our_d
        if diff >= 1:
            any_fast = True
            score = diff * 10 - adj_obst(rx, ry) - (our_d * 0.1)
        else:
            score = diff * 2 - (our_d * 0.5) + (opp_d * 0.1) - adj_obst(rx, ry) * 0.3
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_val = -10**9
    our_curr_d = cheb(sx, sy, tx, ty)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer reducing our distance; also