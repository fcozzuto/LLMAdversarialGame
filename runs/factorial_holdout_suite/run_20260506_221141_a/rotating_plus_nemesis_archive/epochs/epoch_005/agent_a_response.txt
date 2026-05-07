def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = [tuple(p) for p in (observation.get("resources", []) or [])]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    if not resources:
        # Contest: go toward the center of opponent's side, avoiding obstacles by staying.
        tx, ty = (w // 2, 0) if oy > sy else (w // 2, h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not (0 <= nx < w and 0 <= ny < h):
            return [0, 0]
        return [dx, dy]

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    # Avoid obstacles (hard) and prefer moves that reduce distance without stepping into risk zones.
    best_move = (0, 0)
    best_val = None

    # Precompute for speed/clarity
    opp_dists = {(rx, ry): man(ox, oy, rx, ry) for (rx, ry) in resources}

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep us; we treat it as staying.

        step_block_pen = 0
        # Risk if adjacent to obstacle (soft penalty)
        for ax, ay in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1)):
            if (ax, ay) in obstacles:
                step_block_pen += 0.6

        # Choose the single best resource to pursue after this move
        # Objective: maximize our "lead" over opponent, with slight preference for closer turns.
        best_resource_val = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = opp_dists[(rx, ry)]
            # Lead is od - sd; higher means we're closer than opponent
            lead = od - sd
            # If opponent is already much closer, strongly discount that resource (race avoidance).
            if od + 1 < sd:
                lead -= 3.0
            # Mild bias: avoid dead-ends by preferring non-obstacle-near cells.
            val = lead - 0.15 * sd - step_block_pen
            if best_resource_val is None or val > best_resource_val:
                best_resource_val = val

        # Tie-break deterministically: prefer higher value, then smaller sd to that best resource, then lexicographic move.
        if best_val is None or best_resource_val > best_val:
            best_val = best_resource_val
            best_move = (dx, dy)
        elif best_resource_val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]