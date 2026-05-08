def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles)

    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If opponent is sweeping along a row/column, bias to contest that line.
    line_bias_x = 0
    line_bias_y = 0
    if oy == sy:
        line_bias_x = 1
    if ox == sx:
        line_bias_y = 1

    best_move = [0, 0]
    best_obj = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        if not resources:
            tx, ty = (w - 1) // 2, (h - 1) // 2
            ndx = 0 if sx == tx else (1 if tx > sx else -1)
            ndy = 0 if sy == ty else (1 if ty > sy else -1)
            return [ndx, ndy]

        # Maximize how much closer we are than opponent, but with stronger pull to immediate gains.
        local_best = -10**18
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            lead = op_d - my_d  # positive: we are closer
            obj = 2 * lead - my_d  # favor denying first, then fastest pickup
            # Extra contest pressure when aligned with opponent sweep line
            if line_bias_x and ry == sy:
                obj += 0.5
            if line_bias_y and rx == sx:
                obj += 0.5
            # Deterministic tie-break toward smaller distance if equal
            if obj > local_best:
                local_best = obj
                chosen = (my_d, op_d, rx, ry)

        # Deterministic tie-break for equal objective: prefer smaller our distance then toward resources toward opponent direction
        if local_best > best_obj:
            best_obj = local_best
            best_move = [dx, dy]
        elif local_best == best_obj:
            # Compute our distance to the best contested resource from this candidate
            # (Recompute cheaply deterministically)
            mymin = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < mymin:
                    mymin = d
            cur_mymin = mymin

            bx, by = best_move
            qx, qy = sx + bx, sy + by
            best_mymin = 10**9
            for rx, ry in resources:
                d = cheb(qx, qy, rx, ry)
                if d < best_mymin:
                    best_mymin = d

            if cur_mymin < best_mymin:
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]