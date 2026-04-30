def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a target resource that we are relatively closer to than the opponent.
    target = None
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd, -(rx + ry))  # prefer biggest advantage, then closer, then deterministic tie-break
        if best is None or key > best:
            best = key
            target = (rx, ry)

    if target is None:
        # No resources visible: drift toward center while keeping distance from opponent.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tx, ty = int(round(cx)), int(round(cy))
        target = (tx, ty)

    tx, ty = target
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cur_sd = cheb(sx, sy, tx, ty)
    cur_od = cheb(ox, oy, tx, ty)

    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Value: progress to target, keep opponent not gaining advantage, small safety preference.
        prog = cur_sd - nd
        my_adv = (cur_od - nd)  # if we get closer, our advantage increases
        opp_gain = cheb(ox, oy, tx, ty) - cheb(ox, oy, tx, ty)  # zero, kept for clarity
        dist_to_opp = cheb(nx, ny, ox, oy)
        center_bias = -((abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)))
        val = (prog * 10 + my_adv * 3 + dist_to_opp * 0.1 + center_bias * 0.01 + dx * 0.001 + dy * 0.001)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    # If all candidate moves were invalid, stay.
    return best_move if best_move in ([-1, -1],[0,-1],[1,-1],[-1,0],[0,0],[1,0],[-1,1],[0,1],[1,1]) else [