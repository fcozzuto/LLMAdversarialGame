def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            if p is not None and len(p) >= 2:
                obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    opp_cells = set(tuple(t) for t in (observation.get("opponent_territory") or []))
    unclaimed = observation.get("unclaimed_cells") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_score = -10**18

    for c in unclaimed:
        if not c or len(c) < 2:
            continue
        x, y = int(c[0]), int(c[1])
        if not free(x, y):
            continue

        # Prefer cells that are closer to us than to opponent, and near center.
        dself = md(sx, sy, x, y)
        dopp = md(ox, oy, x, y)

        if (x, y) in opp_cells:
            # Being forced onto opponent territory can be okay, but don't prioritize it.
            # Still allow if it is significantly safer to reach.
            pass

        center_dist = md(x, y, cx, cy)
        arrival_bias = (dopp - dself)

        # Strongly discourage cells that are behind the opponent by a lot.
        # Encourage fast expansion and central leverage.
        score = arrival_bias * 10.0 - center_dist * 0.35 - dself * 0.05
        if (x, y) in opp_cells:
            score -= 12.0

        if score > best_score:
            best_score = score
            best = (x, y)

    # If no unclaimed cell is usable, fall back to best neighboring safe move.
    if best is None:
        tx, ty = ox, oy
    else:
        tx, ty = best

    # Head toward target with 8-neighborhood (dx,dy in {-1,0,1}).
    sx0, sy0 = sx, sy
    best_move = [0, 0]
    best_val = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx0 + dx, sy0 + dy
            if not free(nx, ny):
                continue
            # Prefer moves that reduce distance to target and increase distance from opponent.
            v = -md(nx, ny, tx, ty) + 0.3 * md(nx, ny, ox, oy)
            if (nx, ny) in opp_cells:
                v -= 6.0
            if v > best_val:
                best_val = v
                best_move = [dx, dy]

    return best_move