def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources") or []):
        if r is not None and len(r) >= 2:
            rr = (int(r[0]), int(r[1]))
            if rr not in obstacles:
                resources.append(rr)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if resources:
        best_move = (0, 0)
        best_score = 10**18
        # race: prefer targets where we are closer than opponent (or will become so)
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if not legal(nx, ny):
                continue
            # tie-break deterministically by stable ordering: fixed resource iteration order
            local_best = 10**18
            for tx, ty in resources:
                sd = dist(nx, ny, tx, ty)
                od = dist(ox, oy, tx, ty)
                # lower is better: prioritize arriving first, then closer path
                score = sd + 0.6 * (od - sd)  # encourages smaller sd and larger od
                # slight bias toward keeping options open (avoid getting corner-trapped by obstacles)
                score += 0.02 * (abs(tx - (w//2)) + abs(ty - (h//2)))
                if score < local_best:
                    local_best = score
            if local_best < best_score:
                best_score = local_best
                best_move = (dxm, dym)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: move deterministically toward nearest boundary-corner away from opponent
    corners = [(0, 0), (0, h-1), (w-1, 0), (w-1, h-1)]
    # pick corner that maximizes distance from opponent
    best_corner = corners[0]
    best_cd = -1
    for cx, cy in corners:
        cd = dist(ox, oy, cx, cy)
        if cd > best_cd:
            best_cd = cd
            best_corner = (cx, cy)

    tx, ty = best_corner
    best_move = (0, 0)
    best_d = 10**18
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not legal(nx, ny):
            continue
        d = dist(nx, ny, tx, ty)
        if d < best_d:
            best_d = d
            best_move = (dxm, dym)
    return [int(best_move[0]), int(best_move[1])]