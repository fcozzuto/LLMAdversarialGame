def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = set((x, y) for x, y in obstacles)

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    best_res = None
    best_score = None
    for rx, ry in resources:
        ms = cheb((sx, sy), (rx, ry))
        os_ = cheb((ox, oy), (rx, ry))
        # Favor resources we can reach soon and that opponent is not clearly closer to.
        score = ms * 2 + (5 if os_ < ms else 0) + (2 if os_ == ms and (rx + ry) % 2 == 0 else 0) + ((rx * 7 + ry) % 3) * 0.01
        if best_score is None or score < best_score:
            best_score = score
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]

    tx, ty = best_res
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_to_target(x, y):
        dx = abs(x - tx)
        dy = abs(y - ty)
        return dx if dx > dy else dy

    # Also gently discourage stepping near obstacles (if possible).
    obstacle_list = obstacles

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacle_set:
            continue
        dt = dist_to_target(nx, ny)
        do = cheb((nx, ny), (ox, oy))
        near_obs = 0
        if obstacle_list:
            # Count very close obstacles.
            for ex, ey in obstacle_list:
                if abs(nx - ex) <= 1 and abs(ny - ey) <= 1:
                    near_obs += 1
        val = -dt * 10 - do * 0.2 - near_obs * 0.6 + (-0.001 * (nx * 3 + ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]