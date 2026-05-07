def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        da = ax - bx
        db = ay - by
        return da if da >= 0 else -da if da != 0 else 0 if db == 0 else (db if db >= 0 else -db)

    def cheb2(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_adv = None
    best = None
    any_adv = False
    for rx, ry in resources:
        sd = cheb2(sx, sy, rx, ry)
        od = cheb2(ox, oy, rx, ry)
        adv = od - sd  # positive means we are closer
        if not any_adv and adv >= 0:
            any_adv = True
        if best is None:
            best_adv = adv
            best = (rx, ry, sd, od)
        else:
            # prioritize being closer; then closer to target (smaller sd)
            if adv > best_adv or (adv == best_adv and sd < best[2]):
                best_adv = adv
                best = (rx, ry, sd, od)

    # If we are behind everywhere, deny by targeting the closest-to-opponent resource.
    if not any_adv:
        best = None
        for rx, ry in resources:
            sd = cheb2(sx, sy, rx, ry)
            od = cheb2(ox, oy, rx, ry)
            cand = (rx, ry, sd, od)
            if best is None or od < best[3] or (od == best[3] and sd < best[2]):
                best = cand

    tx, ty = best[0], best[1]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    bestm = None
    for dx, dy, nx, ny in moves:
        d_to = cheb2(nx, ny, tx, ty)
        d_opp = cheb2(nx, ny, ox, oy)
        # minimize distance to target; tie-break by maximizing distance from opponent (denial)
        key = (d_to, -d_opp, dx == 0 and dy == 0)
        if bestm is None or key < bestm[0]:
            bestm = (key, [dx, dy])

    return bestm[1]