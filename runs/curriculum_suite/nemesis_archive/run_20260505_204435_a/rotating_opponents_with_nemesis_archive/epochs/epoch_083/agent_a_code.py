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

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    # Intercept/steal: prefer moves that make us closer than opponent to some same resource,
    # and if not, prefer moves that increase opponent's relative disadvantage.
    best = None  # (score tuple, dx, dy)
    rpos_sorted = sorted(set(rpos))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        our_best = None
        for rx, ry in rpos_sorted:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # score: smaller ds, larger (do-ds) ; also break toward nearer opponent resources
            rel = do - ds
            key = (0 if rel > 0 else 1, ds, -rel, do, rx, ry)
            if our_best is None or key < our_best:
                our_best = key

        # Prefer overall stealing/relative advantage, then safer progress
        score = our_best if our_best is not None else (1, 10**9, 0, 10**9, 0, 0)
        candidate = (score, dx, dy)
        if best is None or candidate < best:
            best = candidate

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]