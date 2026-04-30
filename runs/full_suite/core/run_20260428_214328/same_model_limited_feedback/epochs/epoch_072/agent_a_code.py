def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()  # deterministic tie-break

    # Pick a promising resource: prefer where we are relatively closer than opponent.
    best_res = None
    best_gap = -10**9
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cd(sx, sy, rx, ry)
        opd = cd(ox, oy, rx, ry)
        gap = opd - myd
        if gap > best_gap or (gap == best_gap and (rx, ry) < best_res):
            best_gap = gap
            best_res = (rx, ry)

    # If no resources, drift toward opponent to contest center-ish.
    if not best_res:
        tx, ty = (ox + w // 2) // 2, (oy + h // 2) // 2
        best_move = [0, 0]
        best_dist = 10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cd(nx, ny, tx, ty)
            if d < best_dist or (d == best_dist and (dx, dy) < tuple(best_move)):
                best_dist = d
                best_move = [dx, dy]
        return best_move

    rx, ry = best_res

    # Choose move that maximizes immediate advantage toward best_res, with tie-break toward reducing remaining distances.
    best_move = [0, 0]
    best_score = -10**18
    best_tiebreak = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_next = cd(nx, ny, rx, ry)
        opp_here = cd(ox, oy, rx, ry)
        # Primary: relative gain vs opponent for target resource
        score = (opp_here - my_next) * 1000 - my_next

        # Secondary: avoid giving opponent a strictly better shot at any resource
        worst_opp_adv = -10**18
        for prx, pry in resources:
            if (prx, pry) in obstacles:
                continue
            myd = cd(nx, ny, prx, pry)
            opd = cd(ox, oy, prx, pry)
            opp_adv = myd - opd  # higher means opponent farther relative to me
            if opp_adv < worst_opp_adv:
                worst_opp_adv = opp_adv
        score += worst_opp_adv

        tiebreak = (my_next, cd(nx, ny, ox, oy), nx, ny)
        if score > best_score or (score == best_score and (best_tiebreak is None or tiebreak < best_tiebreak)):
            best_score = score
            best_tiebreak = tiebreak
            best_move = [dx, dy]

    return best_move