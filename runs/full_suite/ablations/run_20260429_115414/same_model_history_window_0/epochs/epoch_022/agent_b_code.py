def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]; obstacles = set(tuple(p) for p in observation["obstacles"])
    if not resources:
        return [0, 0]

    def dist2(a, b):
        dx = a[0] - b[0]; dy = a[1] - b[1]
        return dx * dx + dy * dy

    best_res = None
    best_val = None
    for rx, ry in resources:
        md = dist2((sx, sy), (rx, ry))
        od = dist2((ox, oy), (rx, ry))
        val = md - 0.9 * od  # prefer resources relatively closer to us
        if best_val is None or val < best_val:
            best_val = val
            best_res = (rx, ry)

    rx, ry = best_res
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0); best_score = None
    for dx, dy in deltas:
        nx = sx + dx; ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        my_after = dist2((nx, ny), (rx, ry))
        opp_after = dist2((nx, ny), (ox, oy))
        opp_to_res = dist2((ox, oy), (rx, ry))
        score = my_after + 0.15 * opp_after
        if opp_to_res < my_after * 1.05:
            score += 0.25  # slight penalty when opponent also threatens the target
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]