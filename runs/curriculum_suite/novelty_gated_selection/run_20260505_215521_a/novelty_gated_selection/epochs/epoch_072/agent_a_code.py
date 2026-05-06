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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = (0, 0)
        best_val = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                v = -cheb(nx, ny, ox, oy)
                if v > best_val:
                    best_val = v
                    best = (dx, dy)
        return [best[0], best[1]]

    target_dirs = []
    # Precompute best resource to pursue based on relative advantage
    best_res = None
    best_adv = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Higher is better: how much closer we are than the opponent
        adv = (opd - myd) * 10 - myd
        if adv > best_adv:
            best_adv = adv
            best_res = (rx, ry)

    tx, ty = best_res

    # Choose move: greedy toward target with deterministic contest/avoidance
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst):
            continue

        myd = cheb(nx, ny, tx, ty)
        base = -myd

        # Avoid getting too close to opponent unless it improves relative access
        opp_prox = cheb(nx, ny, ox, oy)
        if opp_prox <= 1:
            base -= 3.5

        # If there is a clearly better alternative resource for us, encourage toward it
        rel_best = base
        for rx, ry in resources:
            myd2 = cheb(nx, ny, rx, ry)
            opd2 = cheb(ox, oy, rx, ry)
            adv2 = (opd2 - myd2) * 10 - myd2
            if adv2 > best_adv - 2:  # only consider near-top alternatives
                rel_best = max(rel_best, base + adv2 * 0.01)

        # Small tie-break to maintain momentum toward target direction
        step_align = -abs((tx - nx)) - abs((ty - ny))
        score = rel_best + step_align * 1e-3

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]