def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    w = observation["grid_width"]
    h = observation["grid_height"]

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return (dx*dx + dy*dy)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        if resources:
            # Choose nearest resource to the candidate position (deterministic)
            best_res = None
            best_res_d = 10**18
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                d = dist(nx, ny, rx, ry)
                if d < best_res_d or (d == best_res_d and (rx, ry) < best_res):
                    best_res_d = d
                    best_res = (rx, ry)
            # Move value: prefer closer to nearest resource and farther from opponent
            val = -best_res_d + 0.05 * dist(nx, ny, ox, oy)
            # If the nearest resource would be reached this step, strongly prefer it
            if best_res is not None and (nx, ny) == best_res:
                val += 1e6
        else:
            # No resources: head to center while keeping distance from opponent
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            val = -dist(nx, ny, cx, cy) + 0.1 * dist(nx, ny, ox, oy)

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]