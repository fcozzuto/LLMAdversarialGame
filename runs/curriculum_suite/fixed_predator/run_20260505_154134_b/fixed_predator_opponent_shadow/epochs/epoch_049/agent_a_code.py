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
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    oppcloser_best = None
    oppcloser_key = None
    race_best = None
    race_key = None
    for cx, cy in resources:
        self_d = cheb(sx, sy, cx, cy)
        opp_d = cheb(ox, oy, cx, cy)
        key1 = (opp_d - self_d, -self_d, -cx, -cy)
        if oppcloser_key is None or key1 > oppcloser_key:
            oppcloser_key = key1
            oppcloser_best = (cx, cy)
        key2 = (-self_d, -cx, -cy)  # closer to us
        if race_key is None or key2 > race_key:
            race_key = key2
            race_best = (cx, cy)

    # Mode switch: opportunistic if opponent is meaningfully ahead on some resource.
    mode_target = oppcloser_best
    if oppcloser_key is None:
        mode_target = race_best
    else:
        if oppcloser_key[0] <= 1:
            mode_target = race_best

    tx, ty = mode_target
    # Greedy one-step improvement with obstacle avoidance; deterministic tie-break.
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            d_to_target = cheb(nx, ny, tx, ty)
            d_opp = cheb(nx, ny, ox, oy)
            # Prefer reducing target distance; if tied, prefer increasing opponent distance.
            cand.append((d_to_target, -d_opp, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort()
    return [int(cand[0][2]), int(cand[0][3])]