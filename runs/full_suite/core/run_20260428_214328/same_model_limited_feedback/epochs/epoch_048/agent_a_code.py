def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    cand = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def clamp(x, y):
        if x < 0: x = 0
        if x >= w: x = w - 1
        if y < 0: y = 0
        if y >= h: y = h - 1
        return x, y
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    best = None; best_sc = -10**18
    # Deterministic tie-breaker based on move ordering
    move_order = sorted(cand, key=lambda t: (t[0], t[1]))
    for dx, dy in move_order:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        # Base: go to resource that we can claim "first"
        sc = 0
        # Avoid oscillation: prefer slight movement
        sc -= 0.02 * (dx == 0 and dy == 0)
        sc -= 0.005 * (abs(nx - sx) + abs(ny - sy))
        if resources:
            # Choose best resource to target given resulting position
            local_best = -10**18
            local_second = -10**18
            for i, r in enumerate(resources):
                rx, ry = r
                if (rx, ry) in obstacles:
                    continue
                ds = dist((nx, ny), (rx, ry))
                do = dist((ox, oy), (rx, ry))
                # If we are on it, huge score
                if nx == rx and ny == ry:
                    local_best = 10**9 + i
                    break
                # Prefer resources where we beat opponent by distance
                # Also bias towards nearer resources overall
                takeover = (do - ds)
                val = 20 * takeover - ds
                # Small deterministic preference by index to break ties
                val += -0.001 * i
                if val > local_best:
                    local_second = local_best
                    local_best = val
            # Block intent: if opponent is very close to some resource, move toward nearest such resource
            # Intercept score: reduce opponent advantage
            block = 0
            for i, r in enumerate(resources):
                rx, ry = r
                ds = dist((nx, ny), (rx, ry))
                do = dist((ox, oy), (rx, ry))
                if do <= 2 and ds > do:
                    block = max(block, (do - ds) - 5 - 0.001 * i)
            sc += local_best + 0.5 * block
        # Obstacle proximity penalty: don't get trapped
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    sc -= 0.5
        # Prefer staying away from opponent if no good resource
        if not resources:
            sc -= dist((nx, ny), (ox, oy)) * 0.01
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    if best is None:
        best = [0, 0]
    return best