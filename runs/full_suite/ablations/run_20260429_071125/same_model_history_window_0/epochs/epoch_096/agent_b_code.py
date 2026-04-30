def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def step_towards(tx, ty):
        best = (0, 0)
        best_key = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                if (nx, ny) in obstacles:
                    continue
                k = dist((nx, ny), (tx, ty))
                key = (k, abs(nx - ox) + abs(ny - oy), -(nx + ny))
                if best_key is None or key < best_key:
                    best_key = key
                    best = (dx, dy)
        return [best[0], best[1]]

    if resources:
        best_r = resources[0]
        best_val = None
        for r in resources:
            r = tuple(r)
            if r in obstacles:
                continue
            ds = dist((sx, sy), r)
            do = dist((ox, oy), r)
            val = (do - ds, -ds)  # prioritize resources where opponent is relatively farther and we are closer
            if best_val is None or val > best_val:
                best_val = val
                best_r = r
        tx, ty = best_r
        return step_towards(tx, ty)

    # No resources: drift to center while keeping distance from opponent
    cx, cy = (w - 1) // 2, (h - 1) // 2
    dxdy = step_towards(cx, cy)
    return dxdy