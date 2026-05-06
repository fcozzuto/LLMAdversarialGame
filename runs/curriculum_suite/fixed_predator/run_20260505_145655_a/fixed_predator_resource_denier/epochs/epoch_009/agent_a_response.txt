def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            t = (int(r[0]), int(r[1]))
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    # Deterministic tie-break based on a fixed ordering
    resources_sorted = sorted(resources, key=lambda p: (p[0], p[1]))
    best = [0, 0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate move by choosing the best resource for us under opponent denial pressure.
        move_best = -10**18
        for rx, ry in resources_sorted:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # Want positive advantage: we are closer than opponent; also prefer smaller distances overall.
            # Add small bias for positions that reduce both distances to prevent stalling when denial isn't possible.
            val = (od - sd) * 6 - sd - (sd == 0) * 3
            if val > move_best:
                move_best = val

        # If denial is strong, head toward the most "contested" resource we can still improve.
        # This helps when multiple resources give similar advantage but denial shifts quickly.
        # Compute a secondary check: maximize our improvement in advantage on the best contested target.
        contested_best = -10**18
        for rx, ry in resources_sorted:
            self_now = abs(sx - rx) + abs(sy - ry)
            opp_now = abs(ox - rx) + abs(oy - ry)
            sd = abs(nx - rx) + abs(ny - ry)
            od = opp_now
            imp = (opp_now - sd) - (opp_now - self_now)  # equals self_now - sd
            val2 = imp * 5 - sd
            if val2 > contested_best:
                contested_best = val2

        total = move_best + contested_best * 0.25
        if total > best_val:
            best_val = total
            best = [dx, dy]

    return best