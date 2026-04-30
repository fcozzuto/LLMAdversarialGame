def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dsq(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx*dx + dy*dy

    # If no resources, chase opponent.
    if not resources:
        best = None
        best_u = None
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            u = -dsq(nx, ny, ox, oy)
            if best is None or u > best_u:
                best_u = u
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_u = None

    # Evaluate moves by targeting a resource while also trying to keep the opponent away from it.
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        u = 0.0
        # Progress toward center to avoid oscillation.
        u += -0.03 * (abs(nx - center_x) + abs(ny - center_y))

        # For each resource, pick the "best contest" from this move.
        # Utility: smaller self distance, larger opponent distance.
        best_r_u = None
        for i, r in enumerate(resources):
            rx, ry = r[0], r[1]
            sd = dsq(nx, ny, rx, ry)
            od = dsq(ox, oy, rx, ry)
            # Encourage capturing: high when self is closer and opponent farther.
            r_u = (-sd) + 0.55 * od - 0.001 * i
            if best_r_u is None or r_u > best_r_u:
                best_r_u = r_u
        u += best_r_u

        # Tie-break deterministically: prefer smaller |dx|+|dy|, then lexicographic.
        move_cost = abs(dx) + abs(dy)
        if best_u is None or u > best_u or (u == best_u and (move_cost < (abs(best_move[0]) + abs(best_move[1])) or
                                                              (move_cost == (abs(best_move[0]) + abs(best_move[1])) and (dx, dy) < best_move))):
            best_u = u
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]