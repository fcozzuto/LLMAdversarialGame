def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep_cell(r):
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (q[0], q[1])
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (r[0], r[1])
        return None

    rpos = []
    for r in resources:
        q = rep_cell(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)
    if not rpos:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        cx, cy = min(corners, key=lambda c: max(abs(sx - c[0]), abs(sy - c[1])))
        dx = 1 if cx > sx else (-1 if cx < sx else 0)
        dy = 1 if cy > sy else (-1 if cy < sy else 0)
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        b = y1 - y2
        return abs(a) if abs(a) > abs(b) else abs(b)

    def safe(x, y):
        return inb(x, y) and (x, y) not in blocked

    best_delta = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue

        # Prefer taking resources we can reach sooner than opponent; deter giving them denial power.
        val = 0
        my_best = 10**9
        opp_best = 10**9
        for rx, ry in rpos:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd < my_best:
                my_best = myd
            if opd < opp_best:
                opp_best = opd
            if myd < opd:
                val += 30 - 3 * myd + 2 * (opd - myd)
            elif myd == opd:
                val += 8 - 2 * myd
            else:
                val -= 6 + 2 * (myd - opd)

        # If we're already ahead globally, keep pressure; otherwise move to reduce our lead loss.
        val += (opp_best - my_best)

        # Minor repulsion from opponent to avoid immediate contest escapes by denier.
        dist_to_opp = cheb(nx, ny, ox, oy)
        val -= 0 if dist_to_opp >= 3 else (10 - 3 * dist_to_opp)

        # Tie-break deterministically toward lower x,y deltas then staying.
        if val > best_val or (val == best_val and (dx, dy) < best_delta):
            best_val = val
            best_delta = (dx, dy)

    return [best_delta[0], best_delta[1]]