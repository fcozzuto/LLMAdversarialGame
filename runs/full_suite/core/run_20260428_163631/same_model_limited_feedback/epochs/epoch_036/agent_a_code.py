def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        best = None
        best_key = None
        for dx, dy, nx, ny in valid:
            key = dist((nx, ny), (ox, oy))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose resource where we have the biggest distance advantage; otherwise go to closest resource.
    best_res = None
    best_adv = None
    best_self = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        self_d = dist((sx, sy), (rx, ry))
        opp_d = dist((ox, oy), (rx, ry))
        adv = opp_d - self_d
        if best_adv is None or adv > best_adv or (adv == best_adv and self_d < best_self):
            best_adv = adv
            best_self = self_d
            best_res = (rx, ry)

    tx, ty = best_res

    # If opponent is closer to our chosen target, prioritize moving to reduce their eventual capture chance:
    # slightly prefer moves that increase opponent distance to target while still decreasing ours.
    opp_d0 = dist((ox, oy), (tx, ty))
    best_move = (0, 0)
    best_score = None
    for dx, dy, nx, ny in valid:
        d_self = dist((nx, ny), (tx, ty))
        d_opp = dist((ox, oy), (tx, ty))  # opponent doesn't move this turn
        # Move evaluation: primarily minimize our distance; tie-breaker prefers positions that are farther
        # from opponent (denying near-capture) when no improvement is possible.
        score = (0, 0, 0)
        score = (d_self, -max(abs(nx - ox), abs(ny - oy)))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    # Fallback: if somehow we didn't reduce distance, chase closer to the opponent (more contact pressure).
    if dist((sx + best_move[0], sy + best_move[1]), (tx, ty)) >= dist((sx, sy), (tx, ty)):
        best = None
        best_key = None
        for dx, dy, nx, ny in valid:
            key = dist((nx, ny), (ox, oy))
            if best_key is None or key < best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    return [best_move[0], best_move[1]]