def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    blocked = obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                moves.append((0, dx, dy, sx, sy))
            else:
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                    moves.append((0, dx, dy, nx, ny))
    # ensure stay always available
    if not any(dx == 0 and dy == 0 for _, dx, dy, _, _ in moves):
        moves.append((0, 0, 0, sx, sy))

    # Choose target resource: prioritize those we can reach earlier than opponent, then closer.
    best = None
    bestv = None
    if resources:
        for rx, ry in resources:
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Higher value is better
            v = (do - ds) * 3 - ds
            if best is None or v > bestv:
                bestv = v
                best = (rx, ry)
        tx, ty = best
    else:
        # No visible resources: drift to center
        tx, ty = (w // 2, h // 2)

    # Score moves by how well they reduce distance to target; add small tie-break against opponent proximity.
    best_move = (0, 0)
    best_score = None
    for _, dx, dy, nx, ny in moves:
        d_self = dist((nx, ny), (tx, ty))
        d_opp = dist((ox, oy), (tx, ty))
        # After move, opponent position assumed unchanged; avoid moving closer to opponent itself slightly.
        d_to_opp_self = dist((nx, ny), (ox, oy))
        score = (-d_self) * 10 + (d_to_opp_self) * 0.1 + (-abs(nx - tx) - abs(ny - ty)) * 0.01
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]