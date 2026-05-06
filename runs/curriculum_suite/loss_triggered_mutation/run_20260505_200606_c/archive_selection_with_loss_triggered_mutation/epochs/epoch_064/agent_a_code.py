def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        # Fallback: increase distance from opponent; if cornered, drift toward center.
        cx, cy = w // 2, h // 2
        best = None
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = man(nx, ny, ox, oy) - 0.2 * man(nx, ny, cx, cy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    # Choose a target resource that we can contest (or least likely opponent can steal).
    # Heuristic: for each resource r, score = (opp_dist - self_dist) + small bias to closer resources.
    # Then make a move that maximizes immediate improvement toward the chosen target while not walking into opponent.
    scored = []
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        contested = do - ds  # positive: we're closer
        # Penalize very far resources to keep progress
        val = contested * 3.0 - ds * 0.05 + (rx * 0.001) - (ry * 0.0005)
        scored.append((val, rx, ry))
    scored.sort(reverse=True)
    tx, ty = scored[0][1], scored[0][2]

    # If opponent is already closer to the best target, pick the next one where we're not worse.
    if scored[0][0] < 0 and len(scored) > 1:
        for val, rx, ry in scored[1:4]:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            if do - ds >= -1:
                tx, ty = rx, ry
                break

    cur_ds = man(sx, sy, tx, ty)
    cur_do = man(sx, sy, ox, oy)

    best = None
    bestv = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nds = man(nx, ny, tx, ty)
        ndo = man(nx, ny, ox, oy)
        # Prefer moves that reduce distance to target and increase separation from opponent.
        # Also discourage stepping into squares that give opponent a big advantage (reduce our control).
        opp_to_target = man(nx, ny, tx, ty) - man(ox, oy, tx, ty)
        v = (cur_ds - nds) * 5.0 + (ndo - cur_do) * 1.2 - abs(opp_to_target) * 0.15
        # If opponent is very close, add stronger separation
        if cur_do <= 2:
            v += (ndo - cur_do) * 2.0
        # Tiny deterministic tie-break toward moving "up-left" by comparing coordinates
        v += (-nx * 1e-4) + (-ny * 5e-5)
        if v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]