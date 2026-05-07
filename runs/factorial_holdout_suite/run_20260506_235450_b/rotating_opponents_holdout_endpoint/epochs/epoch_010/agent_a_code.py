def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for a in obstacles:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = 1 if ox > sx else (-1 if ox < sx else 0)
        ty = 1 if oy > sy else (-1 if oy < sy else 0)
        nx, ny = sx + tx, sy + ty
        if inb(nx, ny):
            return [tx, ty]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    best_score = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) in obs:
            continue
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        score = (opp_d - our_d) * 100 - our_d
        if best is None or score > best_score:
            best = (rx, ry)
            best_score = score

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    rx, ry = best
    cur_d = cheb(sx, sy, rx, ry)
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = cheb(nx, ny, rx, ry)
        gain = cur_d - nd
        opp_d = cheb(ox, oy, rx, ry)
        new_our = nd
        contest = (opp_d - new_our) * 100 - new_our
        val = gain * 1000 + contest
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]