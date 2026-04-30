def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def safe(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Deterministic: reduce distance to opponent; if blocked, increase distance.
        best = None
        for ddx, ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if not safe(nx, ny): 
                continue
            d = cheb(nx, ny, ox, oy)
            cand = (d, abs(ddx), abs(ddy), ddx, ddy)
            if best is None or cand < best:
                best = cand
        if best is not None:
            return [best[3], best[4]]
        return [0, 0]

    # Target selection: contest resources where opponent is closer, but prioritize those that are reachable early.
    best_key = None
    best_target = None
    for rx, ry in resources:
        if not inb(rx, ry): 
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # If we are behind (sd>od), value the contest; otherwise still go for nearer-for-us.
        contest = (sd - od)  # positive means we are behind
        # Score key: prefer (more behind) to contest, then prefer closer to us to act.
        # Also slightly prefer lower sd to avoid wandering.
        key = (-(contest if contest > 0 else -contest), sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target if best_target is not None else (sx, sy)

    # Move selection: go toward target if it can beat/maintain advantage; else dodge opponent.
    cur_sd = cheb(sx, sy, tx, ty)
    cur_adv = cheb(sx, sy, ox, oy) - cur_sd  # smaller is better; not a true metric but deterministic heuristic
    best = None
    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not safe(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nadv = cheb(nx, ny, ox, oy) - nsd
        # Primary: minimize nsd (get to resource); secondary: keep/don't worsen advantage vs opponent.
        # If going to target increases distance too much, consider dodge by maximizing distance to opponent.
        opp_dist = cheb(nx, ny, ox, oy)
        cand = (nsd, nadv, -opp_dist, abs(ddx) + abs(ddy), ddx, ddy)
        if best is None or cand < best:
            best = cand

    if best is not None:
        return [best[4], best[5]]

    # If all blocked (unlikely due to engine), fall back deterministically.
    for ddx, ddy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
        nx, ny = sx + ddx, sy + ddy
        if safe(nx, ny):
            return [ddx, ddy]
    return [0, 0]