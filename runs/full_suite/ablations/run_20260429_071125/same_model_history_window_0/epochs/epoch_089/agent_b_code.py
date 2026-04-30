def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        best_t = None
        best_val = -10**9
        for tx, ty in resources:
            ds = dist((sx, sy), (tx, ty))
            do = dist((ox, oy), (tx, ty))
            val = (do - ds) * 10 - ds  # prefer resources we can reach earlier; break ties by closeness
            if val > best_val:
                best_val = val
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        # No visible resources: head to center while keeping away from opponent
        tx, ty = (w // 2, h // 2)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = dist((nx, ny), (tx, ty))
        do2 = dist((ox, oy), (tx, ty))
        # If we move closer, reward strongly; also discourage moving into opponent proximity
        opp_prox = dist((nx, ny), (ox, oy))
        score = -ds2 * 40 + (do2 - ds2) * 8 + opp_prox * 2
        # Small preference for reducing distance to target and not getting stuck
        if (dx, dy) != (0, 0):
            score += 1
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]