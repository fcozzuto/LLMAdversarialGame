def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist_cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def cell_value(x, y):
        if not resources:
            # drift to center
            cx, cy = (gw - 1) // 2, (gh - 1) // 2
            return -dist_cheb(x, y, cx, cy)
        # Prefer resources where we are earlier, otherwise reduce opponent lead.
        best = -10**9
        for rx, ry in resources:
            sd = dist_cheb(x, y, rx, ry)
            od = dist_cheb(ox, oy, rx, ry)
            # tie-break: minimize opponent advantage, encourage being strictly closer
            # also slight preference for being closer to any resource.
            v = (od - sd) * 10 - sd
            if sd == 0:
                v += 1000
            best = v if v > best else best
        return best

    best_move = [0, 0]
    best_v = -10**18
    # deterministic tie-break: smallest dx, then dy in listed order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # small anti-stall: discourage staying still if any resource is nearby
        stall_pen = 0
        if dx == 0 and dy == 0 and resources:
            md = min(dist_cheb(sx, sy, r[0], r[1]) for r in resources)
            stall_pen = -2 if md > 0 else 0
        v = cell_value(nx, ny) + stall_pen
        if v > best_v:
            best_v = v
            best_move = [dx, dy]
    return best_move