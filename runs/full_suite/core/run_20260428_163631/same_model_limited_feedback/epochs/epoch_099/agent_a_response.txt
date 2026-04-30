def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
                valid.append((dx, dy))

    if not valid:
        return [0, 0]

    if not resources:
        # No visible resources: drift toward center while keeping away from opponent if possible.
        cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
        best = (0, 0, -10**9)
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            dcent = -cheb(nx, ny, cx, cy)
            dav = cheb(nx, ny, ox, oy)
            sc = dcent - 0.25 * dav
            if sc > best[2]:
                best = (dx, dy, sc)
        return [best[0], best[1]]

    # Choose a target resource where we have the biggest advantage vs opponent.
    best_t = None
    best_score = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach much sooner; also slightly favor closer overall.
        sc = (do - ds) * 10 - ds
        if sc > best_score:
            best_score = sc
            best_t = (rx, ry)

    rx, ry = best_t if best_t is not None else resources[0]
    # If opponent is adjacent to a resource, prioritize competing with that resource.
    opp_adj = []
    for r in resources:
        ds_r = cheb(ox, oy, r[0], r[1])
        if ds_r <= 1:
            opp_adj.append(r)
    if opp_adj:
        # Compete for the one closest to opponent but with us not too far.
        chosen = None
        chosen_sc = -10**18
        for r in opp_adj:
            ds = cheb(sx, sy, r[0], r[1])
            do = cheb(ox, oy, r[0], r[1])
            sc = (do - ds) * 12 - ds
            if sc > chosen_sc:
                chosen_sc = sc
                chosen = r
        rx, ry = chosen

    # Move one step toward target; break ties by avoiding giving opponent a stronger position.
    best = (0, 0, -10**18)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        d_to = cheb(nx, ny, rx, ry)
        # Penalize moving closer to opponent only if it doesn't help reaching target.
        d_opp = cheb(nx, ny, ox, oy)
        d_opp_now = cheb(sx, sy, ox, oy)
        sc = -d_to * 3 + (d_opp - d_opp_now) * 1 - cheb(nx, ny, rx, ry) * 0.1
        if sc > best[2]:
            best = (dx, dy, sc)

    return [int(best[0]), int(best[1])]