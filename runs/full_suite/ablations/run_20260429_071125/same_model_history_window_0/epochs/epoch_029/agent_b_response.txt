def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    x = sx
    y = sy

    move_list = [
        (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1)
    ]

    def inb(px, py):
        return 0 <= px < w and 0 <= py < h

    def d2(px, py, rx, ry):
        dx = px - rx
        dy = py - ry
        return dx * dx + dy * dy

    # If no resources, just drift away from opponent while avoiding obstacles
    if not resources:
        best = None
        best_val = -10**18
        for dx, dy in move_list:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            val = d2(nx, ny, ox, oy)  # maximize separation
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in move_list:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate move by how much it improves our lead to the best resource
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            self_dist = d2(nx, ny, rx, ry)
            opp_dist = d2(ox, oy, rx, ry)
            # Prefer resources where opponent is relatively farther than we are
            val = (opp_dist - self_dist) * 100 - self_dist
            if val > local_best:
                local_best = val
        # Tie-break: prefer smaller self distance to closest resource, then fixed order
        if local_best > best_val:
            best_val = local_best
            best_move = (dx, dy)
        elif local_best == best_val:
            # deterministic tie-break
            closest_self = min(d2(nx, ny, rx, ry) for rx, ry in resources if (rx, ry) not in obstacles)
            best_closest = min(d2(x + best_move[0], y + best_move[1], rx, ry) for rx, ry in resources if (rx, ry) not in obstacles)
            if closest_self < best_closest:
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]