def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    # candidates
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def d2(a, b):
        dx = a[0] - b[0]; dy = a[1] - b[1]
        return dx*dx + dy*dy

    # No resources: drift to center while keeping away from opponent
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy, nx, ny in candidates:
            score = d2((nx, ny), (cx, cy)) + 0.2 * d2((nx, ny), (ox, oy))
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Greedy toward best resource with opponent repulsion and slight tie-breaks
    best = None
    for dx, dy, nx, ny in candidates:
        step_score = 0.0
        # Prefer moves that reduce distance to the "best" resource
        # Evaluate each resource and take the minimum combined cost for that move
        move_min = None
        for rx, ry in resources:
            # cost: distance to resource + avoid getting too close to opponent (to contest less)
            cost = d2((nx, ny), (rx, ry)) + 0.15 * (2* d2((nx, ny), (ox, oy)))
            # discourage stepping into positions close to obstacles by local proxy
            # (simple: if adjacent to many obstacles, slightly worse)
            adj = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx+ax, ny+ay) in obstacles:
                        adj += 1
            cost += 0.05 * adj
            if move_min is None or cost < move_min:
                move_min = cost
        # If we're already on a resource, prefer to stay/collect deterministically
        if (sx, sy) in set(tuple(p) for p in resources):
            # If possible, stay; otherwise nearest move that still doesn't worsen too much
            move_min = -1.0 if (nx, ny) == (sx, sy) else move_min
        step_score = move_min
        # tie-break: prefer staying still if tied, else smallest dx then dy
        key = (step_score,
               0 if (dx == 0 and dy == 0) else 1,
               abs(dx), abs(dy), dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]