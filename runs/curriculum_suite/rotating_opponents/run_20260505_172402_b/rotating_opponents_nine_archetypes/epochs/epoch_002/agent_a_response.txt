def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles", [])
    obs_set = {(p[0], p[1]) for p in obstacles}
    resources = observation.get("resources", [])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def clamp_move(nx, ny):
        if not inb(nx, ny) or (nx, ny) in obs_set:
            return sx, sy
        return nx, ny

    def obst_prox(x, y):
        c = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if (x + ex, y + ey) in obs_set:
                    c += 1
        return c

    # Target selection: prefer resources we can realistically reach before opponent.
    if resources:
        best = None
        for rx, ry in resources:
            my_d = abs(rx - sx) + abs(ry - sy)
            op_d = abs(rx - ox) + abs(ry - oy)
            if my_d <= op_d:
                score = my_d - 0.1 * op_d  # prioritize being closer
            else:
                score = my_d + 0.7 * (op_d - my_d)  # discourage contested/too-late spots
            if best is None or score < best:
                best = score
                tx, ty = rx, ry
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Move selection: minimize distance to target, strongly avoid obstacles, avoid approaching opponent too closely.
    best_cost = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = clamp_move(sx + dx, sy + dy)
        # If we "clamped" due to obstacle/out-of-bounds, treat it as costly by proximity + target distance (strong avoid).
        hit = (nx, ny) == (sx, sy) and ((not inb(sx + dx, sy + dy)) or (sx + dx, sy + dy) in obs_set)
        dist_t = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        dist_o = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        cost = dist_t + 7.0 * obst_prox(nx, ny) - 0.08 * dist_o
        if hit:
            cost += 1e6
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]