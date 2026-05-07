def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Drift away from opponent while staying in bounds
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                s = man((nx, ny), (ox, oy)) - (abs(nx - (w - 1)) + abs(ny - (h - 1))) * 0.01
                if s > best[0]:
                    best = (s, dx, dy)
        return [int(best[1]), int(best[2])]

    # Prefer moves that let us arrive earlier than opponent to some resource
    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_best = -10**18
        for rx, ry in resources:
            d_self = man((nx, ny), (rx, ry))
            d_opp = man((ox, oy), (rx, ry))
            # We win this resource if we are closer; encourage immediate pickup and "deny" opponent
            lead = d_opp - d_self  # higher is better
            # If we can pick now (d_self==0), strongly prioritize
            val = lead * 10.0 - d_self * 1.5
            # Slightly prefer resources closer to our side centerline to reduce pathing ties
            val -= (rx - (w * 0.5))**2 * 0.001 + (ry - (h * 0.5))**2 * 0.001
            if val > my_best:
                my_best = val

        # Choose move with best resource race advantage; tie-break deterministically toward increasing x then y
        if my_best > best_val or (my_best == best_val and (dx, dy) > best_move):
            best_val = my_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]