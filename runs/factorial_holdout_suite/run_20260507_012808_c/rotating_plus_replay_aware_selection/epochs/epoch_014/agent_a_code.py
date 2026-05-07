def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    resources = observation.get("resources", []) or []
    if resources:
        best = None
        best_val = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # Choose move that most improves "resource advantage": opponent further than us.
            # Score: (min opp-dist - min self-dist), then prefer being closer to a resource.
            min_self = 10**9
            min_opp = 10**9
            min_denial = -10**9
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                if ds < min_self: min_self = ds
                if do < min_opp: min_opp = do
                # Deny score favors resources where our move tightens the gap vs opponent.
                gap = do - ds
                if gap > min_denial: min_denial = gap
            val = (min_opp - min_self, -min_self, min_denial)
            if best_val is None or val > best_val:
                best_val = val
                best = [dx, dy]
        return best

    # No visible resources: move to maximize distance from opponent (and avoid being trapped).
    best = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, ox, oy)
        # Prefer moves that keep some mobility next step.
        mobility = 0
        for ddx, ddy in dirs:
            xx, yy = nx + ddx, ny + ddy
            if ok(xx, yy):
                mobility += 1
        val = (d, mobility)
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]
    return best