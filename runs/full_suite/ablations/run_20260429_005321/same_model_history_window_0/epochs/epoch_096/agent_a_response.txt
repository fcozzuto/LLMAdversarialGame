def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_val = -10**18

    def in_bounds(x, y):
        return 0 <= x < W and 0 <= y < H

    def manh(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    if not resources:
        # If no resources, move to maximize distance from opponent (stall safely)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            val = manh((nx, ny), (ox, oy))
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Strategic switch: prioritize resources where we can be earlier than opponent, otherwise deny by heading to contested line
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Find best contested target: maximize (opp_dist - self_dist) for any resource
        best_contested = -10**18
        closest_self = 10**9
        closest_opp = 10**9
        for rx, ry in resources:
            d_self = manh((nx, ny), (rx, ry))
            d_opp = manh((ox, oy), (rx, ry))
            if d_self < closest_self:
                closest_self = d_self
            if d_opp < closest_opp:
                closest_opp = d_opp
            cont = d_opp - d_self
            if cont > best_contested:
                best_contested = cont

        # Deny factor: move to increase opponent's distance to our most likely next target
        # Compute target again as the one giving best_contested
        target_dx = 0
        target_dy = 0
        # approximate target: nearest resource to us from new position
        trx, try_ = resources[0]
        best_ds = 10**9
        for rx, ry in resources:
            d_self = manh((nx, ny), (rx, ry))
            if d_self < best_ds:
                best_ds = d_self
                trx, try_ = rx, ry
        opp_to_target = manh((ox, oy), (trx, try_))
        self_to_target = best_ds
        # small improvement preference: closer to nearest and farther from opponent
        val = 2000 * best_contested + 20 * (opp_to_target - self_to_target) + 5 * manh((nx, ny), (ox, oy)) - closest_self
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]