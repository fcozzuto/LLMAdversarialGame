def choose_move(observation):
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0
    if w <= 0 or h <= 0:
        return [0, 0]

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                v = -man(nx, ny, ox, oy)
                if v > bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    # Interception/race heuristic:
    # Prefer resources where opponent is near but we can close the gap after this move.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Encourage not letting the opponent increase their lead.
        # Value uses (opp_dist - self_dist): higher means we're closer than opponent.
        # Also add a small term to push toward the nearest reachable resource.
        local_best = -10**18
        nearest = 10**9
        nearest_to_opp = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            gap = od - sd  # positive => we are closer to this resource
            if gap > local_best:
                local_best = gap
            if sd < nearest:
                nearest = sd
            if od < nearest_to_opp:
                nearest_to_opp = od

        # If opponent is close to some resource, race it; otherwise just compress distance to nearest.
        # Penalize moving away from both (using sum of distances).
        opp_closeness = 0
        for rx, ry in resources:
            od = man(ox, oy, rx, ry)
            if od < nearest_to_opp + 1:
                opp_closeness = od  # deterministic tie: overwrites to smallest encountered last; loop order is deterministic
                break

        v = (local_best * 100) - (nearest * 3) + (nearest_to_opp - man(nx, ny, ox, oy)) * 0.5
        v -= man(nx, ny, ox, oy) * 0.1

        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    return best_move