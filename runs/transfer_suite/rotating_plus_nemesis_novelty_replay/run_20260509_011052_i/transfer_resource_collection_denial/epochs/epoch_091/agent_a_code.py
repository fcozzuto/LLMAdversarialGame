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

    def step_options():
        opts = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    opts.append((dx, dy))
        return opts if opts else [(0, 0)]

    def toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    # Choose target by advantage: (opp_distance - our_distance) with tie-break toward nearer resources
    best = None
    best_adv = -10**9
    for rx, ry in resources:
        od = cheb(ox, oy, rx, ry)
        sd = cheb(sx, sy, rx, ry)
        adv = od - sd
        # Encourage taking when we can match/beat opponent; otherwise prefer reducing opponent's options
        val = (adv * 1000) - sd
        if val > best_adv:
            best_adv = val
            best = (rx, ry)

    tx, ty = best
    dxt, dyt = toward(tx, ty)

    # If the direct step is blocked (or suboptimal), evaluate all local moves deterministically
    opts = step_options()
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in opts:
        nx, ny = sx + dx, sy + dy
        # primary: move closer to chosen target
        dist_to = cheb(nx, ny, tx, ty)
        # secondary: deny opponent by also moving toward states where they are farther from their nearest target
        opp_near = min(resources, key=lambda p: cheb(ox, oy, p[0], p[1]))
        opp_dist_next = cheb(ox, oy, opp_near[0], opp_near[1])
        score = (-dist_to * 10) + (opp_dist_next)  # opp_dist_next constant-ish but keeps stability
        # slight bias to keep progressing toward target direction
        score += -cheb(nx, ny, sx + dxt, sy + dyt)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]