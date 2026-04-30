def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def best_move(tx, ty):
        deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best = (10**9, None)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), (tx, ty))
            # Avoid stepping into obvious confrontation if it doesn't improve target
            opp_d = dist((nx, ny), (ox, oy))
            score = d - 0.15 * opp_d + (0.02 if (dx == 0 and dy == 0) else 0)
            if score < best[0]:
                best = (score, (dx, dy))
        return best[1] if best[1] is not None else [0, 0]

    # Choose a target resource by relative advantage (our closeness minus opponent closeness)
    if resources:
        best_r = None
        best_val = 10**9
        for rx, ry in resources:
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources we are significantly closer to; also slightly discourage far resources
            val = (ds - 0.9 * do) + 0.05 * ds
            if val < best_val or (val == best_val and (rx, ry) < best_r):
                best_val = val
                best_r = (rx, ry)
        tx, ty = best_r
        return best_move(tx, ty)

    # If no resources remain, try to press toward opponent while avoiding obstacles
    return best_move(ox, oy)