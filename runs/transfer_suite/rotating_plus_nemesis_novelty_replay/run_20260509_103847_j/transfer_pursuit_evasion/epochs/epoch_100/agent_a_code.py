def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    resources = observation.get("resources") or []
    rpos = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                rpos.append((x, y))
        elif isinstance(r, dict):
            x, y = int(r.get("x", -1)), int(r.get("y", -1))
            if 0 <= x < w and 0 <= y < h:
                rpos.append((x, y))
    moves = [(-1, 0), (0, -1), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    best_move = (0, 0)
    best_val = -10**18
    has_res = bool(rpos)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if has_res:
            d_me = 10**18
            d_opp = 10**18
            for rx, ry in rpos:
                dm = dist(nx, ny, rx, ry)
                do = dist(ox, oy, rx, ry)
                if dm < d_me:
                    d_me = dm
                    d_opp_for_best = do
                else:
                    d_opp_for_best = do if dm == d_me else d_opp_for_best
            # Prefer nearing nearest resource, and prefer resources opponent is farther from.
            val = (-d_me) + (-0.5 * max(0, d_opp_for_best - d_me)) + (-0.1 * dist(nx, ny, ox, oy))
        else:
            # If no resources, maximize distance from opponent.
            val = dist(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]