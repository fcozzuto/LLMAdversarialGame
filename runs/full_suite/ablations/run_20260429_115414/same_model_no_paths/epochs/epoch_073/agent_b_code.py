def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    oppd = cheb(sx, sy, ox, oy)

    target = None
    best_t = -10**18
    if resources:
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            contest = (od - sd)  # positive if we are closer
            # prefer nearer target when contest is similar
            val = contest * 100 - sd + (1 if (rx + ry) % 2 == 0 else 0)
            if val > best_t:
                best_t = val
                target = (rx, ry)
    else:
        # no visible resources: drift to opponent's opposite diagonal to reduce access
        target = (w - 1 - ox, h - 1 - oy)

    tx, ty = target
    best_move = (0, 0)
    best_v = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # if we can reach target sooner than opponent, aggressively reduce our distance
        v = 0
        v += (nod - nsd) * 200  # win contest pressure
        v += -(nsd) * 3         # also get it sooner
        # slight repulsion from opponent when contests are weak
        if oppd > 0:
            v += (cheb(nx, ny, ox, oy) - oppd) * 1.5
        # avoid parking on parity traps: prefer moves that change parity less often
        v += -0.1 * abs(((nx + ny) & 1) - ((sx + sy) & 1))
        if v > best_v:
            best_v = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]