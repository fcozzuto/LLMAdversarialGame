def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation["resources"] if observation["resources"] else []
    obstacles = observation["obstacles"] if observation["obstacles"] else []
    obstacle_set = set((p[0], p[1]) for p in obstacles)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    res_set = set((p[0], p[1]) for p in resources)

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obstacle_set:
            continue
        if (nx, ny) == (ox, oy):
            continue

        total = 0
        best_r = None
        best_r_val = -10**9
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            v = (od - sd)
            if sd == 0:
                v += 50
            if v > best_r_val:
                best_r_val = v
                best_r = (rx, ry)
        if resources:
            # Encourage being closer to the currently most competitive resource
            rx, ry = best_r
            dist = abs(nx - rx) + abs(ny - ry)
            total = best_r_val - 0.05 * dist
        else:
            total = -0.01 * (abs(nx - ox) + abs(ny - oy))

        # Mild preference to move toward center when no clear target
        total -= 0.001 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
        if total > best_val:
            best_val = total
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]