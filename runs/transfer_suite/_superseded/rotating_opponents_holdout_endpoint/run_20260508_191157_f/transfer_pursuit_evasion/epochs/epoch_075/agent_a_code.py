def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    role = observation.get("self_role", "pursuer")
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # For pursuer, aim to constrain opponent toward its nearest corner while staying close.
    # For evader, aim to escape to its farthest corner while maximizing distance.
    if role == "pursuer":
        target_corner = min(corners, key=lambda c: man(ox, oy, c[0], c[1]))
    else:
        target_corner = max(corners, key=lambda c: man(ox, oy, c[0], c[1]))

    best_dx, best_dy = 0, 0
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue

        d_to_opp = man(nx, ny, ox, oy)
        d_corner = man(nx, ny, target_corner[0], target_corner[1])
        d_opp_corner = man(ox, oy, target_corner[0], target_corner[1])  # constant per turn

        # Tie-breakers: avoid getting stuck near obstacles by slightly preferring moves
        # with more free surrounding cells.
        free_n = 0
        for adx, ady in deltas:
            tx, ty = nx + adx, ny + ady
            if in_bounds(tx, ty) and not blocked(tx, ty):
                free_n += 1

        if role == "pursuer":
            # Strongly minimize distance to opponent; then move to corner-constraint target.
            # Also prefer moves that do NOT increase opponent's distance to its target corner (proxy).
            opp_corner_proxy = d_opp_corner  # can't predict; keep constant for determinism
            val = d_to_opp * 1000 + d_corner + opp_corner_proxy * 0.001 - free_n * 2.0
            better = best_val is None or val < best_val
        else:
            # Evader: maximize distance to opponent; then head for escape corner; prefer mobility.
            val = -d_to_opp * 1000 - d_corner - free_n * 2.0 + (man(nx, ny, ox, oy) == 0) * 1e9
            better = best_val is None or val < best_val

        if better:
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]