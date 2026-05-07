def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_score = None

    # Pick a "primary" target deterministically: resource with best (opp closer first?).
    # We then evaluate one-step moves against all resources for better interception.
    primary = None
    primary_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd)  # larger advantage, then smaller distance
        if primary is None or key > primary_key:
            primary = (rx, ry)
            primary_key = key

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        # If landing on resource, prioritize heavily.
        landing = 1 if (nx, ny) in set((r[0], r[1]) for r in resources) else 0

        best_adv = -10**9
        best_tdist = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive => we are closer after this move
            if adv > best_adv or (adv == best_adv and myd < best_tdist):
                best_adv = adv
                best_tdist = myd

        # Steer toward primary target if advantages are similar.
        ptd = cheb(nx, ny, primary[0], primary[1])
        cur = (landing * 1000000 + best_adv * 1000 - ptd, -best_tdist, nx, ny)
        if best_score is None or cur > best_score:
            best_score = cur
            best_move = [dx, dy]

    return best_move