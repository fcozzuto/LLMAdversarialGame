def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in (observation.get("resources", []) or [])]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_resource():
        if not resources:
            return None
        best = None
        for rx, ry in resources:
            sd = man((sx, sy), (rx, ry))
            od = man((ox, oy), (rx, ry))
            gain = od - sd  # positive means we are closer
            # Prefer securing resources we can reach first; otherwise reduce opponent advantage.
            key = (-(gain), sd, od, rx, ry)
            # Smaller key better due to leading minus gain.
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        return best[1]

    target = best_resource()

    def step_toward(tx, ty):
        # Compute desired direction; then choose a safe move that best matches it.
        desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
        desired_dy = 0 if ty == sy else (1 if ty > sy else -1)
        cands = []
        for ddx, ddy in deltas:
            nx, ny = sx + ddx, sy + ddy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            dt = man((nx, ny), (tx, ty))
            do = man((nx, ny), (ox, oy))
            align = abs(ddx - desired_dx) + abs(ddy - desired_dy)
            # primary: get closer to target, secondary: keep away from opponent, tertiary: alignment and determinism
            cands.append((dt, -do, align, ddx, ddy))
        if not cands:
            return [0, 0]
        cands.sort()
        return [cands[0][3], cands[0][4]]

    if target is not None:
        return step_toward(target[0], target[1])

    # No resources: move deterministically toward safer center while not moving into obstacles.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    return step_toward(cx, cy)