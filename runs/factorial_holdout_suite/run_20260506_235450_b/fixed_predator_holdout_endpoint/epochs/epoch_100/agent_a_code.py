def choose_move(observation):
    def ti(v):
        try:
            return int(v)
        except:
            return 0

    w = ti(observation.get("grid_width", 8)) or 8
    h = ti(observation.get("grid_height", 8)) or 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = ti(sp[0]), ti(sp[1])
    ox, oy = ti(op[0]), ti(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        x = y = None
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
        elif isinstance(p, dict) and "x" in p and "y" in p:
            x, y = ti(p.get("x")), ti(p.get("y"))
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x = y = None
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = ti(r[0]), ti(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = ti(r.get("x")), ti(r.get("y"))
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        ay = b - d
        if ay < 0: ay = -ay
        return ax if ax >= ay else ay

    def best_target():
        best = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; if contested, still pick by our advantage.
            key = (od - sd, -sd, -(rx + ry))
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        return best[1]

    tx, ty = best_target()

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (None, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        # Score: progress to target, deny opponent progress, and lightly avoid getting stuck.
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # If moving makes us relatively closer while also not letting opp gain (via diagonal parity), it's better.
        rel = opp_d - self_d
        # Also include: move that increases distance between us and opponent (denial by separation).
        sep = cheb(nx, ny, ox, oy)
        # Tie-break deterministically by favoring smaller manhattan-like towards target.
        md = abs(nx - tx) + abs(ny - ty)
        key = (rel, sep, -self_d, -md)
        if best_move[0] is None or key > best_move[0]:
            best_move = (key, (dx, dy))

    if best_move[1] is None:
        return [0, 0]
    dx, dy = best_move[1]
    return [int(dx), int(dy)]