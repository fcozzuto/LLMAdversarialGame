def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if resources:
        self_t = min(resources, key=lambda r: (cheb((x, y), r), r[0], r[1]))
        opp_t = min(resources, key=lambda r: (cheb((ox, oy), r), r[0], r[1]))
        self_cur = cheb((x, y), self_t)
        opp_cur = cheb((ox, oy), opp_t)
    else:
        cx, cy = w // 2, h // 2
        self_t = (cx, cy)
        opp_t = (ox, oy)
        self_cur = cheb((x, y), self_t)
        opp_cur = 0

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_dx, best_dy = 0, 0
    best_val = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            ns = cheb((nx, ny), self_t)
            # assume opponent keeps targeting same resource this turn (deterministic proxy)
            no = opp_cur - 0  # keep constant baseline; only reward moves that force away via our blocking proxy
            # Proxy block: if we move to be closer to opponent's target than they currently are, it's likely contested.
            block = 0
            if cheb((nx, ny), opp_t) < cheb((ox, oy), opp_t):
                block = 2
            # Proxy pressure: prefer increasing opponent-target distance from our move position (makes contest harder).
            opp_proxy = cheb((nx, ny), opp_t)
            val = (self_cur - ns) + (opp_proxy - cheb((ox, oy), opp_t)) + block
        else:
            ns = cheb((nx, ny), self_t)
            # no resources: go center while slightly distancing from opponent
            opp_dist = cheb((nx, ny), (ox, oy))
            val = (self_cur - ns) + (opp_dist - cheb((x, y), (ox, oy)))*0.5

        # Tie-break deterministically: prefer smaller |dx|+|dy| then lexicographic dx,dy
        key = (val, - (abs(dx) + abs(dy)), -dx, -dy)
        if best_val is None or key > best_key:
            best_val = val
            best_key = key
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]