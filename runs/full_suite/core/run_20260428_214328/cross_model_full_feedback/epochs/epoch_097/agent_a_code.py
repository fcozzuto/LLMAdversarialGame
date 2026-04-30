def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp = (ox, oy)
    me = (sx, sy)

    target = None
    best_gap = None
    if resources:
        for r in resources:
            rd = cheb(me, r)
            od = cheb(opp, r)
            gap = od - rd  # positive => we are closer
            if best_gap is None or gap > best_gap or (gap == best_gap and (rd < cheb(me, target))):
                target = r
                best_gap = gap

    if target is None:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        target = (cx, cy)

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        new_me = (nx, ny)
        our_d = cheb(new_me, target)
        cur_our_d = cheb(me, target)
        if our_d > cur_our_d:
            penalty = 1
        else:
            penalty = 0

        new_opp_d = cheb(new_me, opp)

        # Encourage grabbing tempo and staying away from opponent when contested.
        if resources:
            res_d = cheb(new_me, target)
            opp_d = cheb(opp, target)
            contested = (opp_d - res_d) <= 0  # we are not ahead on target
        else:
            contested = False

        # Key: maximize safety, then minimize distance to target, then minimize moving "backward".
        key = (new_opp_d if not contested else new_opp_d * 2 - penalty, -our_d, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]