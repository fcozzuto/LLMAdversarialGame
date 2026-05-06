def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target_from(posx, posy):
        # Prefer a resource where we are strictly closer; if none, prefer least-bad contest (minimize opp-self gap)
        best = None
        bestv = -10**18
        for rx, ry in resources:
            dS = cheb(posx, posy, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            gap = dO - dS  # positive => we can reach first
            # slight urgency: closer resources get extra weight; also encourage denying (negative gap)
            v = gap * 1000 - (dS * 3) - (0 if gap > 0 else 200)
            # deterministic tie-break: lexicographic by (rx,ry)
            if v > bestv or (v == bestv and (rx, ry) < best):
                bestv = v
                best = (rx, ry)
        return best, bestv

    # If no resources, drift away from opponent while maximizing distance from their corner-ish direction
    if not resources:
        tx, ty = w - 1, h - 1
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy) * 1000 - cheb(nx, ny, tx, ty)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Main: for each move, evaluate whether we can win a contest now, and also whether we reduce opponent's best future pressure.
    # (We approximate "opponent future" by comparing their current distances; enough for deterministic denial.)
    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        # Immediate target choice based on our post-move position
        (rx, ry), v_take = best_target_from(nx, ny)

        # Denial term: if there exists a resource where opponent is closer than us currently, try to move to increase our edge there.
        v_deny = 0
        for rj in range(len(resources)):
            rrx, rry = resources[rj]
            dS = cheb(nx, ny, rrx, rry)
            dO = cheb(ox, oy, rrx, rry)
            gap = dS - dO  # negative => we are closer than opponent (denial / catching)
            # Encourage making gap more positive if opponent currently leads (gap = dS-dO >0), or more negative if we can flip.
            v_deny += -gap * 20

        # Staying still penalty unless it improves contest
        stay_pen = 0 if (dx != 0 or dy != 0) else 80

        # Extra bias: don't move into opponent's "direct line" too much (approx by minimizing cheb between us and opponent after move)
        v_sep = cheb(nx, ny, ox, oy) * 5

        # Deterministic tie-break: slight preference for moves with smaller (dx,dy) lexicographically
        v = v_take + v_deny + v_sep - stay_pen
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]