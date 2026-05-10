def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    ox2 = int(ox)
    oy2 = int(oy)
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose the single best "contested" resource from this next position.
        best_adv = -10**18
        best_myd = 10**9
        best_opd = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox2, oy2, rx, ry)
            adv = opd - myd  # positive means we get it sooner
            if adv > best_adv or (adv == best_adv and (myd < best_myd or (myd == best_myd and opd < best_opd))):
                best_adv, best_myd, best_opd = adv, myd, opd

        # Scoring: prefer moves that maximize advantage; if all are negative,
        # still pick the closest resource and prefer denying opponent proximity.
        val = (best_adv * 1000) - best_myd
        # Small deterministic tie-breaker: prefer moves that get closer to the best resource even if tied.
        val -= best_opd // 4
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]