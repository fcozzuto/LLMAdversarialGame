def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    candidates = []
    for (dx, dy) in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        candidates.append((dx, dy, nx, ny))

    # Focus on a small deterministic set of resources: closest by our chebyshev distance.
    dlist = []
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        dlist.append((d, rx, ry))
    dlist.sort()
    top = dlist[:min(6, len(dlist))]
    top_res = [(rx, ry) for _, rx, ry in top]

    # Move evaluation: maximize the best immediate capture advantage; tie-break by closing distance.
    # Additionally bias slightly toward moving toward the center (reduce being cornered by shadow archetypes).
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    best = None
    best_val = None

    for dx, dy, nx, ny in candidates:
        center_bias = -0.01 * (abs(nx - cx) + abs(ny - cy))
        best_adv = -10**18
        best_self_dist = 10**18
        best_opp_close = 10**18

        for rx, ry in top_res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer/equal than opponent in 1-step capture sense
            if adv > best_adv or (adv == best_adv and (ds < best_self_dist or (ds == best_self_dist and do < best_opp_close))):
                best_adv = adv
                best_self_dist = ds
                best_opp_close = do

        # Strongly prefer positive advantage; otherwise still prefer least opponent pressure and shortest path.
        val = (best_adv * 1000000) + (-best_self_dist * 10) + (-best_opp_close) + center_bias
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]