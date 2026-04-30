def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    grid_w = observation.get("grid_width", 8)
    grid_h = observation.get("grid_height", 8)
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = -10**9

    opp_pos = (ox, oy)
    obstacle_list = obstacles

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= grid_w or ny >= grid_h:
            continue
        if (nx, ny) in obstacle_list:
            continue

        my_pos = (nx, ny)
        # Choose a contested target: maximize advantage (opp dist - my dist) with slight preference for closeness.
        cur = -10**9
        for rx, ry in resources:
            if (rx, ry) in obstacle_list:
                continue
            d_self = dist(my_pos, (rx, ry))
            d_opp = dist(opp_pos, (rx, ry))
            adv = d_opp - d_self  # positive means we are closer
            val = adv * 10 - d_self
            if val > cur:
                cur = val
        # If we can immediately reach a resource, prioritize strongly.
        immediate = 0
        for rx, ry in resources:
            if (rx, ry) in obstacle_list:
                continue
            if dist(my_pos, (rx, ry)) == 0:
                immediate = 1000
                break
            if dist(my_pos, (rx, ry)) == 1:
                immediate = 100
        cur += immediate

        # Small tie-break: prefer not moving away from current best target (more stable).
        if cur > best_val:
            best_val = cur
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]