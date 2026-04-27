def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not in_bounds(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Prefer resource we can reach first; if contested, block by approaching it from a direction that increases opponent distance.
    best_move = (10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not in_bounds(nx, ny):
            continue

        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            if my_d < my_best: my_best = my_d
            if op_d < opp_best: opp_best = op_d

        # Main score: smaller my_best is better.
        # Bonus if we have a "lead" over opponent to the nearest resource.
        lead = opp_best - my_best  # positive means advantage for nearest resource
        # Secondary: avoid stepping into tight region near opponent (encourages indirect blocking rather than head-on).
        tight = cheb(nx, ny, ox, oy)

        # Extra: if this move directly reduces distance to the single best target (sorted deterministically by position).
        # Deterministic tie-breaking among resources with same metric.
        target_best = resources[0]
        target_best_score = None
        for rx, ry in resources:
            s = (cheb(mx, my, rx, ry) - cheb(ox, oy, rx, ry), rx, ry)
            if target_best_score is None or s < target_best_score:
                target_best_score = s
                target_best = (rx, ry)
        tr, tc = target_best
        direct = cheb(nx, ny, tr, tc)

        score = my_best * 10 + (-lead) * 3 + tight * 0.25 + direct * 0.05
        # Lower is better. Deterministic tie-break using (dx, dy) lexicographic.
        if score < best_move[0] or (score == best_move[0] and (dx, dy) < (best_move[1], best_move[2])):
            best_move = (score, dx, dy)

    return [best_move[1], best_move[2]]