def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    ti = int(observation.get("turn_index", 0))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = [0, 0]
    best_sc = -10**18

    # Deterministic tie-breaker ordering shift
    shift = ti % 9
    order = moves[shift:] + moves[:shift]

    # Precompute obstacle-avoidance for next step
    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    # If no resources, head toward opponent while keeping distance from obstacles
    if not resources:
        for dx, dy in order:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # prefer moving closer to opponent, but avoid being adjacent to obstacles only slightly
            sc = -cheb(nx, ny, ox, oy)
            if sc > best_sc:
                best_sc = sc
                best = [dx, dy]
        return [best[0], best[1]]

    # Otherwise, maximize "take priority": we want to be closer to some resource than opponent
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Compute best target resource for this next position
        take = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Higher if we are closer than opponent; reward strong lead, penalize being behind
            lead = opd - myd
            # Encourage reaching likely resources (smaller myd) and discourage giving opponent immediate options
            sc_r = (lead * 4) - (myd) + (opd // 8)
            if sc_r > take:
                take = sc_r

        # Anti-follow: discourage moves that allow opponent to instantly take the same best target
        # Estimate by checking if opponent could step to a cell that is very close to any resource
        opp_threat = -10**18
        for odx, ody in moves:
            tx, ty = ox + odx, oy + ody
            if not valid(tx, ty):
                continue
            best_tx = -10**18
            for rx, ry in resources:
                d = cheb(tx, ty, rx, ry)
                best_tx = max(best_tx, -d)
            opp_threat = max(opp_threat, best_tx)

        # Obstacle "soft" avoidance: count valid adjacent cells after our move
        neigh = 0
        for ax, ay in moves:
            if valid(nx + ax, ny + ay):
                neigh += 1

        # Combine: lead to a resource, reduce opponent threat (less adjacency to resources), keep mobility
        sc = take + (neigh * 3) + (opp_threat // 20)
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return [int(best[0]), int(best[1])]