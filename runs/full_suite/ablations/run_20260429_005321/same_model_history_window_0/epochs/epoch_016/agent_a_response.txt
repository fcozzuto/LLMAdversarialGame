def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]
    obs_set = set((x, y) for x, y in obstacles)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev distance

    # If no resources, just move to reduce distance to center-ish
    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        best_val = None
        for dx, dy, nx, ny in candidates:
            val = -dist((nx, ny), (cx, cy)) + 0.05 * dist((ox, oy), (nx, ny))
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = None
    for dx, dy, nx, ny in candidates:
        # Advantage over opponent towards the best resource
        best_adv = None
        best_res_dist = None
        for rx, ry in resources:
            d_self = dist((nx, ny), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            adv = d_opp - d_self  # higher means we are closer
            if best_adv is None or adv > best_adv or (adv == best_adv and (best_res_dist is None or d_self < best_res_dist)):
                best_adv = adv
                best_res_dist = d_self
        # Tie-break: avoid moving toward opponent by too much (block lightly)
        move_to_opp = dist((nx, ny), (ox, oy))
        self_pos_value = -best_res_dist + 0.02 * move_to_opp
        # Penalize if opponent can immediately reach the same closest resource (approx)
        # Estimate by comparing our best target advantage sign
        val = self_pos_value + 0.3 * best_adv
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]