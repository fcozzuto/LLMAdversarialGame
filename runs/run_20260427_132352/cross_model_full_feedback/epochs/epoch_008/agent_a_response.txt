def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def dist(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    # If no resources, drift toward center while not approaching opponent.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            d = dist(nx, ny, tx, ty)
            da = dist(nx, ny, ox, oy)
            score = d * 10 - da  # prefer closer to center, farther from opponent
            tie = (nx * 17 + ny * 31) % 997
            key = (score, tie)
            if best is None or key < best:
                best = key
        if best is None:
            return [0, 0]
        # recover move deterministically from key by re-scanning
        best_key = best
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny) and ((dist(nx, ny, tx, ty) * 10 - dist(nx, ny, ox, oy)), (nx * 17 + ny * 31) % 997) == best_key:
                return [dx, dy]
        return [0, 0]

    # Pick a "contested" target: maximize (opp_dist - my_dist) (relative advantage).
    best_res = None
    best_adv = -10**9
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        adv = opd - myd
        # deterministic tie: prefer lower my distance, then lexicographic resource
        if adv > best_adv or (adv == best_adv and (myd < dist(sx, sy, best_res[0], best_res[1]) if best_res else True)):
            best_adv = adv
            best_res = (rx, ry)

    tx, ty = best_res
    # Evaluate moves by stealing progress from opponent on the same contested target,
    # while avoiding getting trapped (obstacles) and not suicidally closing on opponent.
    best_key = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        myd = dist(nx, ny, tx, ty)
        opd = dist(ox, oy, tx, ty)
        # my improvement vs current
        cur_myd = dist(sx, sy, tx, ty)
        improve = cur_myd - myd
        # discourage moving closer to opponent unless it improves contest significantly
        my_to_opp = dist(nx, ny, ox, oy)
        cur_to_opp = dist(sx, sy, ox, oy)
        opp_danger = (cur_to_opp - my_to_opp)  # positive if I get closer
        # tie-breaker encourages exploring deterministically
        tie = (nx * 29 + ny * 7 + observation.get("turn_index", 0) * 3) % 997
        # Key: minimize opponent-relative advantage loss; primary: minimize myd
        # plus: large penalty if I move closer to opponent without improving
        score = myd * 100 - (opd - myd) * 10 - improve * 25 + (opp_danger > 0) * opp_danger * 60 + tie
        if best_key is None or score < best_key:
            best_key = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]