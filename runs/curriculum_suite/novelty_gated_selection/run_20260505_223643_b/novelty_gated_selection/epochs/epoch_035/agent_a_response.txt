def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def nearest_dist(pos, targets):
        best = 10**9
        for t in targets:
            d = man(pos, t)
            if d < best:
                best = d
        return best

    # Opponent-denier: assume opponent heads to their nearest remaining resource.
    opp_target = min(resources, key=lambda r: man((ox, oy), r))
    # Our primary target: resource that minimizes our distance, but we’ll evaluate candidates against opp_target.
    self_target = min(resources, key=lambda r: man((sx, oy), r))

    def step_valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    best_mv = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not step_valid(nx, ny):
            continue

        # Distances from candidate position
        self_d_self = man((nx, ny), self_target)
        self_d_any = nearest_dist((nx, ny), resources)
        opp_d_opp = man((nx, ny), opp_target)

        # Evaluate: increase opponent's distance to their target while decreasing ours,
        # also keep us close to some resource to avoid getting stuck in denial-only moves.
        base = (opp_d_opp - self_d_self) * 2.0
        closeness = (self_d_any * -1.0)
        # Small tie-break: prefer moves that move generally toward opponent’s target direction to "contest" its lane.
        dir_bias = - (abs((nx - sx)) + abs((ny - sy))) * 0.01

        val = base + closeness + dir_bias
        if val > best_val:
            best_val = val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]