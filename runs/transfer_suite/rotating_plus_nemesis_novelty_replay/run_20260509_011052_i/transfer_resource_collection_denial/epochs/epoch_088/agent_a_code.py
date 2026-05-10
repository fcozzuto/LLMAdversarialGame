def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; lightly prefer central-ish and avoid opponent proximity.
        reach_adv = od - sd
        picked_bias = 0
        if (ry == sy): picked_bias += 1
        if (rx == sx): picked_bias += 1
        score = reach_adv * 10 - sd + picked_bias
        # Deterministic tie-break: smaller target x then y
        key = (-(reach_adv * 10 - sd + picked_bias), rx, ry)
        if best is None or key < best:
            best = key
            best_score = (rx, ry)

    tx, ty = best_score

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic order preference: closer first, then x,y
    bestm = None
    bestmk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # If opponent can also threaten target quickly, bias toward faster own approach.
        if resources:
            od_next = cheb(ox, oy, tx, ty)
            sd_next = d
        else:
            od_next = 9999
            sd_next = d
        threat = 0
        if od_next <= sd_next:
            threat = 6
        mk = (d + threat, nx, ny)
        if bestm is None or mk < bestmk:
            bestm = [dx, dy]
            bestmk = mk

    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]