def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [w - 1, h - 1]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        dx = 0
        if sx < ox: dx = 1
        elif sx > ox: dx = -1
        dy = 0
        if sy < oy: dy = 1
        elif sy > oy: dy = -1
        return [dx, dy]

    def score_from(px, py):
        best = -10**18
        for rx, ry in resources:
            d_my = cheb(px, py, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Big reward if we are closer (or can tie by next step); otherwise prefer denying.
            adv = d_op - d_my
            s = adv * 1000 - d_my
            # Tie-break deterministically towards nearer resources and "more central" squares.
            s += (3.5 - abs(rx - 3.5)) * 2 + (3.5 - abs(ry - 3.5)) * 2
            if s > best:
                best = s
        return best

    best_move = [0, 0]
    best_val = -10**18
    for mx, my in dirs:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        val = score_from(nx, ny)
        # Additional micro-signal: avoid moving directly into opponent range when not beneficial.
        opp_range = cheb(nx, ny, ox, oy)
        val -= (opp_range == 1) * 25 + (opp_range == 0) * 200
        if val > best_val:
            best_val = val
            best_move = [mx, my]

    return [int(best_move[0]), int(best_move[1])]