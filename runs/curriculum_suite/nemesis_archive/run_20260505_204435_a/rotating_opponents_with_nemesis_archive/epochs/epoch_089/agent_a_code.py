def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def rep_cell(r):
        if isinstance(r, dict):
            q = r.get("position")
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                return (int(q[0]), int(q[1]))
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            return (int(r[0]), int(r[1]))
        return None

    rpos = []
    for r in resources:
        q = rep_cell(r)
        if q and inb(q[0], q[1]) and q not in blocked:
            rpos.append(q)
    if not rpos:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)  # Chebyshev

    best = None
    best_sc = -10**18
    rpos_sorted = sorted(rpos, key=lambda t: (t[0] * 8 + t[1]))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        best_r_sc = -10**18
        for rx, ry in rpos_sorted:
            myd = dist(nx, ny, rx, ry)
            old_my = dist(sx, sy, rx, ry)
            if myd > old_my + 1:
                continue  # avoid big regressions
            od = dist(ox, oy, rx, ry)
            # Prefer capturing/approaching nearer resources, and resources where opponent is relatively farther.
            sc = (-myd * 10) + ((od - myd) * 2) + ((old_my - myd) * 3)
            # Small preference to aim slightly away from obstacles "edge" not needed; deterministic tie-break below
            if sc > best_r_sc:
                best_r_sc = sc
        if best_r_sc > best_sc:
            best_sc = best_r_sc
            best = (dx, dy)
        elif best_r_sc == best_sc and best is not None:
            # deterministic tie-break: closer to opponent => less likely to be blocked by opponent path
            cur = (abs(nx - ox) + abs(ny - oy), dx, dy)
            prev = (abs((sx + best[0]) - ox) + abs((sy + best[1]) - oy), best[0], best[1])
            if cur < prev:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]