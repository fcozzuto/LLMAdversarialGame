def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    target_cells = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            target_cells.append((nx, ny, dx, dy))
    if not target_cells:
        target_cells = [(sx, sy, 0, 0)]

    def dist(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    best_move = (0, 0, 0.0, 0.0)  # (dx,dy,primary,secondary)
    if not resources:
        # Deterministically drift toward the center while avoiding obstacles
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for nx, ny, dx, dy in target_cells:
            primary = -dist((nx, ny), (tx, ty))
            secondary = -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty))
            if primary > best_move[2] or (primary == best_move[2] and secondary > best_move[3]):
                best_move = (dx, dy, primary, secondary)
        return [best_move[0], best_move[1]]

    # Choose move that maximizes immediate "possession edge" for the best resource
    # Advantage = opponent_dist - self_dist; higher is better.
    for nx, ny, dx, dy in target_cells:
        my_best_adv = -10**9
        my_best_near = 10**9
        for rx, ry in resources:
            myd = dist((nx, ny), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            adv = opd - myd
            if adv > my_best_adv or (adv == my_best_adv and myd < my_best_near):
                my_best_adv = adv
                my_best_near = myd

        # Secondary: prefer not to wander; also slightly prefer closing on the closest resource overall
        close_overall = min(dist((nx, ny), r) for r in resources)
        primary = my_best_adv
        secondary = -close_overall

        if primary > best_move[2] or (primary == best_move[2] and secondary > best_move[3]):
            best_move = (dx, dy, primary, secondary)

    return [best_move[0], best_move[1]]