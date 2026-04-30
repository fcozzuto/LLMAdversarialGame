def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        resources = [(sx, sy)]

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    move_order = []
    for i, (dx, dy) in enumerate(moves):
        # slight deterministic preference to advance rather than stay
        pref = 0 if (dx == 0 and dy == 0) else 1
        move_order.append((-(pref), i, dx, dy))
    move_order.sort()

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best = (0, 0, -10**18)  # dx,dy,score
    my = (sx, sy)
    opp = (ox, oy)

    # Strategy: pick move that helps us be first to a resource vs opponent.
    # Score favors (opp_dist - self_dist): larger means we can arrive first.
    # Add secondary preference: being closer to a high-leverage target when ties occur.
    for _, _, dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        cand = (nx, ny)

        # compute best target advantage from this candidate
        best_adv = -10**18
        best_tdist = 10**18
        best_prim = 10**18
        for t in resources:
            sd = cheb(cand, t)
            od = cheb(opp, t)
            adv = od - sd  # want large
            prim = sd
            # prioritize blocking: if we are about to get it, also account for opponent distance
            if adv > best_adv or (adv == best_adv and prim < best_prim) or (adv == best_adv and prim == best_prim and od < best_tdist):
                best_adv = adv
                best_prim = prim
                best_tdist = od

        # If opponent is close to a nearby resource, we also want to not drift away from our nearest contested point
        # (secondary: keep self distance low to the currently best resource from current position).
        # Deterministic tie-break with position-based bias toward center.
        cx_bias = -abs(nx - (w - 1) / 2.0) - abs(ny - (h - 1) / 2.0)
        score = best_adv * 1000 - best_prim + cx_bias

        if score > best[2]:
            best = (dx, dy, score)

    return [int(best[0]), int(best[1])]