def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    def cheb(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 if d1 > d2 else d2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Choose a target resource with "steal priority": strong preference to where we can be closer,
    # but avoid chasing if opponent is much closer (resource denial).
    target = None
    best_key = None
    if res:
        for rx, ry in res:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # If opponent is closer, penalize heavily; else reward advantage.
            adv = od - sd  # positive => we are closer
            penalty = 0
            if od < sd:
                penalty = (sd - od) * (sd + 1) + (od + 1)
            key = (penalty, -adv, sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                target = (rx, ry)

    # If no resources, move to increase spacing and keep stable.
    tx, ty = (target if target is not None else (sx, sy))

    best_move = (0, 0)
    best_score = None
    cur_to_t = cheb(sx, sy, tx, ty)
    cur_to_o = cheb(sx, sy, ox, oy)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        nt = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, ox, oy)
        # Primary: reduce distance to target; Secondary: avoid opponent (denial counterplay);
        # Tertiary: prefer not getting stuck (don't increase target distance too much).
        score = (nt * 10 - no * 3, nt, -(dx == 0 and dy == 0), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    # If all moves invalid (unlikely), stay.
    if best_move is None:
        return [0, 0]
    # Ensure return ints in {-1,0,1}.
    return [int(best_move[0]), int(best_move[1])]