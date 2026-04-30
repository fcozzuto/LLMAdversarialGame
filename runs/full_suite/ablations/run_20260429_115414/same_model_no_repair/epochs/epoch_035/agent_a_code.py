def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obs9 = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]

    def risk(x, y):
        r = 0
        for dx, dy in obs9:
            nx, ny = x + dx, y + dy
            if (nx, ny) in blocked:
                r += 1
        return r

    # Pick a target resource: maximize opponent advantage minus being in a "risky" corridor.
    target = None
    if resources:
        best = None  # (score, -selfd, tx, ty)
        for rx, ry in resources:
            if not inb(rx, ry) or (rx, ry) in blocked:
                continue
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Small penalty if target is near obstacles to reduce dead-ends.
            pen = risk(rx, ry) * 0.1
            adv = od - sd
            cand = (adv - pen, -sd, rx, ry)
            if best is None or cand > best:
                best = cand
        if best is not None:
            _, _, tx, ty = best
            target = (tx, ty)

    if target is None:
        # No resources: move to the "safer" center-biased cell away from opponent.
        tx, ty = w // 2, h // 2
        best_move = (0, 0)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            dself = cheb(nx, ny, tx, ty)
            do = cheb(nx, ny, ox, oy)
            cand = (-(dself) + 0.2 * do - 0.1 * risk(nx, ny), -dself, dx, dy)
            if best is None or cand > best:
                best = cand
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = target
    # Choose move that keeps advantage on the chosen target; break ties by safety and staying closer.
    best = None  # (score, -sd, do, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Also consider "shadowing": prefer not letting opponent reduce its own advantage next.
        # (Approx: compare candidate sd to current sd, and penalize if we move closer to opponent.)
        sd0 = cheb(sx, sy, tx, ty)
        opp_closeness = cheb(nx, ny, ox, oy)
        cand_score = (od - sd) * 1.0 - 0.6 * (sd - sd0) - 0.15 * risk(nx, ny) - 0.05 * opp_closeness
        cand = (cand_score, -sd, od, dx, dy)
        if best is None or cand > best:
            best = cand

    return [best[3], best[4]]