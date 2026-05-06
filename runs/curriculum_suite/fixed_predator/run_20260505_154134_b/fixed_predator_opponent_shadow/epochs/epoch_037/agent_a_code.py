def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_key = None

    # If no resources, just drift to increase distance from opponent deterministically.
    if not resources:
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            # Prefer increasing Chebyshev distance from opponent
            key = (cheb(nx, ny, ox, oy), -nx, -ny)
            if best_key is None or key > best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move

    # Evaluate one-step lookahead: choose move maximizing resource-ownership advantage.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if nx == sx and ny == sy:
            stay_pen = 1
        else:
            stay_pen = 0

        # Advantage over opponent: (opp_d - self_d) higher is better.
        # Also encourage progress by penalizing remaining distance to the best target.
        best_adv = None
        best_dist = None
        best_tie = None
        for cx, cy in resources:
            self_d = cheb(nx, ny, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            adv = opp_d - self_d
            dist = self_d
            # Prefer higher advantage; then nearer; then deterministic by coords
            tie = (adv, -dist, -cx, -cy)
            if best_adv is None or tie > best_tie:
                best_adv = adv
                best_dist = dist
                best_tie = tie

        # Additional deterrent: if we can get closer to opponent's best resources, keep pressure.
        # Use current opponent-to-nodes distance difference as a small secondary term.
        opp_pressure = 0
        for cx, cy in resources:
            sd = cheb(nx, ny, cx, cy)
            od = cheb(ox, oy, cx, cy)
            if od <= sd:
                opp_pressure += 1
        key = (best_adv, -best_dist, -opp_pressure, -stay_pen, -nx, -ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move