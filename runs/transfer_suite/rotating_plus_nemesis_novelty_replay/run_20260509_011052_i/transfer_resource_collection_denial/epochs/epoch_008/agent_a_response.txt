def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obs

    def mdist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If a resource list exists but is empty, treat as none
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        # choose a valid step that approaches opponent
        moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
        best = (10**9, [0, 0])
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            dist = mdist(nx, ny, ox, oy)
            if dist < best[0]:
                best = (dist, [ddx, ddy])
        if best[1] != [0, 0]:
            return best[1]
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_score = 10**18
    best_move = [0, 0]

    # Deterministic tie-break: prefer lower dx, then lower dy
    for ddx, ddy in sorted(moves, key=lambda t: (t[0], t[1])):
        nx, ny = sx + ddx, sy + ddy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        # evaluate how soon we can secure a resource before opponent
        cur = 10**18
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            d_me = mdist(nx, ny, rx, ry)
            d_op = mdist(ox, oy, rx, ry)
            # If opponent is closer, heavily penalize; encourage taking otherwise-contested targets
            penalty = 0
            if d_op < d_me:
                penalty = (d_me - d_op + 1) * 4
            # Prefer nearer resources, but also slightly prefer those closer to capture than opponent
            val = d_me + penalty + (0.1 * d_op)
            if val < cur:
                cur = val
        # small additional preference: don't drift away from resources overall
        # (tie-break handled later)
        if cur < best_score:
            best_score = cur
            best_move = [ddx, ddy]

    return best_move