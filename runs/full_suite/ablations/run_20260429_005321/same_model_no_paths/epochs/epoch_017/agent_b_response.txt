def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if resources and any(sx == rx and sy == ry for rx, ry in resources):
        return [0, 0]

    # Opponent's closest resource becomes the "threat"; we try to deny it.
    if resources:
        threat = min(resources, key=lambda r: (cheb(ox, oy, r[0], r[1]), r[0], r[1]))
        trx, try_ = threat
    else:
        trx, try_ = 0, 0

    def resource_score(cx, cy):
        if not resources: return -10**9
        # Prefer a resource where we are at least as close as the opponent, else minimize their lead.
        best = None
        for rx, ry in resources:
            ds = cheb(cx, cy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive => we are closer
            val = (-(lead), ds + do, rx, ry)  # deterministic tie-break
            # We invert inside later; keep deterministic ordering
            if best is None or val < best[0]:
                best = (val, lead, ds, do)
        # Convert to maximization
        _, lead, ds, do = best
        return lead * 100 - ds * 2 + (0 if do > ds else 10)

    def threat_denial(cx, cy):
        # If we can get close to the threat, do it; otherwise drift to safer resources.
        ds = cheb(cx, cy, trx, try_)
        do = cheb(ox, oy, trx, try_)
        # Deny when we can match or beat them; otherwise avoid proximity to their fastest path.
        return (do - ds) * 80 - ds * 5

    def obstacle_risk(cx, cy):
        # Prefer keeping open space (local obstacle adjacency).
        risk = 0
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in obstacles:
                risk += 1
        return -risk * 3

    # Choose the move maximizing a blended objective.
    best = (-(10**18), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = 0
        val += obstacle_risk(nx, ny)
        if resources:
            val += resource_score(nx, ny)
            val += threat_denial(nx, ny)
        # Extra deterministic tie-break: prefer moves that reduce distance to threat if tied.
        val2 = val, -cheb(nx, ny, trx, try_), nx, ny
        if val2 > best:
            best = val2
            best_move = (dx, dy)

    # If all candidates invalid (shouldn't happen), stay still.
    return list(best_move) if best_move else [0, 0]