def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    res = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    res = [(int(x), int(y)) for x, y in res]
    obs_set = {(int(x), int(y)) for x, y in obs}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                return [dx, dy]
        return [0, 0]

    # Target resources using deterministic tie-breaking.
    # Score a move by how much it improves our race vs opponent for the best remaining resource.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        # For each resource, estimate whether we are closer than opponent and by how much.
        # Also add a small penalty for being farther from the globally closest resource after move.
        local_best = -10**18
        closest_after = 10**9
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < closest_after:
                closest_after = ds
            # Prefer resources we can reach no later than opponent; break ties toward resources we are closer to.
            race = (do - ds)  # positive means we are closer than opponent
            reachable_bonus = 20 if ds <= do else 0
            # Slight preference to move toward resources that are nearer by ourselves.
            val = race * 10 + reachable_bonus - ds
            # Tie-break deterministically by coordinates (minimize lexicographic).
            if val > local_best or (val == local_best and (rx, ry) < best_move):
                local_best = val

        # Encourage reducing our distance to some resource and discouraging giving opponent an advantage.
        val = local_best + (-2 * closest_after)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]