def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    opp_role = (observation.get("opponent_role", "") or "").lower()

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def cell_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best = None
    best_val = None
    rem = int(observation.get("remaining_resource_count", len(res)) or len(res))
    urgency = 1.0 if rem <= 4 else 0.3

    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive if we are closer
        align = 0
        if rx == sx: align += 1
        if ry == sy: align += 1
        if ("sweep" in opp_role) and (ry == oy): align += 1.2  # deny opponent row-sweep
        # If we can't beat opponent, still allow earlier/cheaper contest with urgency near end.
        contest = (lead * 2.0) + urgency * (lead >= 0) * 2.0
        # Prefer nearer targets with slight bias to alignment for faster acquisition.
        val = (contest, -ds, align, -abs(rx - rx), rx, ry)
        if best is None or val > best_val:
            best = (rx, ry)
            best_val = val

    tx, ty = best
    cxands = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                cxands.append((0, 0))
                continue
            nx, ny = sx + dx, sy + dy
            if cell_ok(nx, ny):
                cxands.append((dx, dy))

    if not cxands:
        return [0, 0]

    # Greedy one-step improvement toward chosen target; if tied, avoid stepping into positions
    # where opponent is significantly closer next.
    best_move = (0, 0)
    best_score = None
    for dx, dy in cxands:
        nx, ny = sx + dx, sy + dy
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        move_lead = opd - myd
        # tiny deterministic tie-breaker favors reducing x-difference first
        tieb = -(abs((nx - tx))) - abs((ny - ty)) * 0.001
        score = (move_lead, -myd, tieb)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]