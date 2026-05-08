def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    resource_set = set((r[0], r[1]) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2)

    # Immediate capture
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) in resource_set:
            return [dx, dy]

    # Score each move: prefer resources we beat; otherwise deny by making opponent slower on their best resource.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = 0
        # Small bias: keep moving toward center line of remaining resources deterministically
        if resources:
            # choose a deterministic anchor resource by lexicographic order
            rx0, ry0 = sorted(resources)[0]
            val -= 0.001 * cheb(nx, ny, rx0, ry0)

        self_best = None
        opp_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            t_self = cheb(nx, ny, rx, ry)
            t_opp = cheb(ox, oy, rx, ry)
            margin = t_opp - t_self  # positive means we reach first
            # Favor reaching earlier strongly; tie-break by smaller t_self
            cand_self = (margin, -t_self)
            if self_best is None or cand_self > self_best:
                self_best = cand_self
            # For denial, estimate what opponent's best target is (independent of our motion)
            cand_opp = ( -t_opp, (rx, ry) )
            if opp_best is None or cand_opp > opp_best:
                opp_best = cand_opp

        # If we can win a resource, maximize the winning margin and urgency
        if self_best:
            margin, nt = self_best
            val += 1000 * margin + 2 * (-nt)

        # Denial: if opponent is closer to some resource than we are, move to reduce their margin
        deny = 0
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            t_self = cheb(nx, ny, rx, ry)
            t_opp = cheb(ox, oy, rx, ry)
            if t_opp < t_self:
                # We can't guarantee capture; try to approach that resource to increase t_self closer to t_opp
                deny += (t_self - t_opp)
        val += 0.5 * deny

        # Deterministic tie-breaker: prefer not increasing distance to nearest resource
        min_d_now = min(cheb(nx, ny, r[0], r[1]) for r in resources)
        min_d_cur = min(cheb(sx, sy, r[0], r[1]) for r in resources)
        val += 0.01 * (min_d_cur - min_d_now)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]