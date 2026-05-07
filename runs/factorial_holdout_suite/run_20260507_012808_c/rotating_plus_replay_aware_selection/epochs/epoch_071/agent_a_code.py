def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    ox, oy = observation["opponent_position"]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        ddx = 0 if tx == sx else (1 if tx > sx else -1)
        ddy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + ddx, sy + ddy
        return [ddx, ddy] if valid(nx, ny) else [0, 0]

    best = None
    best_key = (-10**18, -10**18, -10**18, 0)

    for mx, my in dirs:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            nx, ny = sx, sy
            mx, my = 0, 0

        win_count = 0
        best_margin = -10**18
        best_self_d = 10**18
        best_opp_d = 10**18

        for rx, ry in resources:
            ds = d(nx, ny, rx, ry)
            do = d(ox, oy, rx, ry)
            margin = do - ds  # positive => we reach no later than opp
            if ds <= do:
                win_count += 1
                if margin > best_margin:
                    best_margin = margin
                    best_self_d = ds
                    best_opp_d = do
                elif margin == best_margin and ds < best_self_d:
                    best_self_d = ds
                    best_opp_d = do
            else:
                if do < best_opp_d:
                    best_opp_d = do

        # Tie-break: maximize ability to win soon; then prefer smaller self distance.
        # Penalize if we likely lose all resources from this move.
        if win_count > 0:
            key = (win_count, best_margin, -best_self_d, 0)
        else:
            # Try to approach a resource where we are closest, even if not winning immediately.
            closest_ds = 10**18
            closest_do = 10**18
            for rx, ry in resources:
                ds = d(nx, ny, rx, ry)
                do = d(ox, oy, rx, ry)
                if ds < closest_ds or (ds == closest_ds and do < closest_do):
                    closest_ds, closest_do = ds, do
            key = (0, closest_do - closest_ds, -closest_ds, 0)

        if key > best_key:
            best_key = key
            best = [mx, my]

    return best if best is not None else [0, 0]