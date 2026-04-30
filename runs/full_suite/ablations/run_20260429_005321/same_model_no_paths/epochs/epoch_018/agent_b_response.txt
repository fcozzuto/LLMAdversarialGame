def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    # If we're standing on a resource, stay.
    for rx, ry in resources:
        if sx == rx and sy == ry:
            return [0, 0]

    # If no resources exist, maximize distance from opponent while avoiding obstacles.
    if not resources:
        best = (0, 0, -10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            val = cheb(nx, ny, ox, oy)
            if val > best[2]:
                best = (dx, dy, val)
        return [best[0], best[1]]

    # Threat is the opponent-closest resource.
    threat = min(resources, key=lambda r: (cheb(ox, oy, r[0], r[1]), r[0], r[1]))
    tx, ty = threat[0], threat[1]
    opp_threat_d = cheb(ox, oy, tx, ty)

    best = (0, 0, -10**18)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate move by: (1) deny resources opponent is closest to, (2) secure best reachable advantage.
        # For each resource, advantage = (opponent_distance - self_distance). Higher is better.
        # Also penalize being far from any resource.
        best_adv = -10**18
        min_self_d = 10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv:
                best_adv = adv
            if sd < min_self_d:
                min_self_d = sd

        # Urgency: if opponent is very close to the threat, prioritize minimizing our distance to it.
        # If opponent is close (d<=1), block harder (higher weight).
        urg = 6.0 if opp_threat_d <= 1 else (2.5 if opp_threat_d == 2 else 1.0)
        threat_term = urg * (opp_threat_d - cheb(nx, ny, tx, ty))

        # Small deterministic tie-break using position ordering.
        tie = - (nx * 0.01 + ny * 0.001)
        val = 2.0 * best_adv - 0.6 * min_self_d + threat_term + tie

        if val > best[2]:
            best = (dx, dy, val)

    return [best[0], best[1]]