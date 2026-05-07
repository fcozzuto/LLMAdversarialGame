def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    resources = observation.get("resources") or []
    candidates = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obst and 0 <= rx < w and 0 <= ry < h:
                ds = cheb(sx, sy, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # Prefer taking when we are closer; contest when opponent is much closer.
                # Also slightly prefer resources that are "ahead" of opponent toward ours.
                lead = do - ds
                contest = 4 if do <= ds else 0
                opp_line = 1 if ry == oy else 0
                candidates.append((lead + contest + opp_line, -ds, rx, ry))

    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    _, _, tx, ty = candidates[0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    best_move = [0, 0]
    best_val = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            # If we step onto a resource, prioritize heavily.
            step_gain = 0
            for r in resources:
                if isinstance(r, (list, tuple)) and len(r) >= 2:
                    rx, ry = int(r[0]), int(r[1])
                    if rx == nx and ry == ny and (rx, ry) not in obst:
                        step_gain = 100
                        break
            # Mildly avoid giving opponent an easy immediate capture by keeping distance from them.
            opp_d = cheb(nx, ny, ox, oy)
            val = step_gain - d + 0.02 * opp_d
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]