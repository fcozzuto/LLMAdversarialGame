def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                x, y = int(q[0]), int(q[1])
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            continue
        if inb(x, y) and (x, y) not in blocked:
            rpos.append((x, y))
    if not rpos:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    step_pref = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    # Pick a target resource where we have a distance advantage (self much closer than opponent).
    cand = []
    for (rx, ry) in rpos:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer: smaller ds, much smaller than do. Deterministic tie-breaker by coords.
        cand.append((ds - do, ds, rx, ry))
    cand.sort()
    targets = [(c[3], c[2]) for c in cand[:3]]

    # Evaluate immediate moves by resulting step-to-best-target advantage, plus avoid blocked cells.
    best_move = (0, 0)
    best_val = None
    for dx, dy in step_pref:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        # Also avoid moving into squares adjacent to obstacles if possible (soft penalty).
        adj_block = 0
        for mx, my in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            ax, ay = nx + mx, ny + my
            if (ax, ay) in blocked:
                adj_block = 1
                break

        # Determine best target after this move.
        best_t = None
        for tx, ty in targets:
            ds2 = cheb(nx, ny, tx, ty)
            do2 = cheb(ox, oy, tx, ty)
            val = (ds2 - do2, ds2, tx, ty)
            if best_t is None or val < best_t:
                best_t = val
        val = best_t
        # Objective: minimize (self-opponent distance gap, self distance), then coords. Add adjacency penalty.
        score = (val[0], val[1] + (1 if adj_block else 0), val[2], val[3])
        if best_val is None or score < best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]