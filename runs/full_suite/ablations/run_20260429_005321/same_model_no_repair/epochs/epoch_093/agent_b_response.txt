def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def near_obst(x, y):
        c = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + dx, y + dy) in obst:
                c += 1
        return c

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # If resources remain, race to a target that's relatively more favorable than what the opponent can take sooner.
    # If no resources, move toward opponent's side while avoiding obstacles.
    if resources:
        best_target = None
        best_val = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer targets that are closer for us and farther for opponent; lightly prefer safer approach lanes.
            near = near_obst(rx, ry)
            val = (ds - 0.9 * do) + 0.15 * near
            if best_val is None or val < best_val:
                best_val = val
                best_target = (rx, ry)

        rx, ry = best_target
        # Choose move that improves distance to the target while reducing collision risk and opponent shadowing.
        best_move = None
        best_score = None
        for dx, dy, nx, ny in legal:
            ds_next = cheb(nx, ny, rx, ry)
            do_next = cheb(ox, oy, rx, ry)
            block = 0
            # Small bias for moving toward opponent if we are not behind on the target.
            if ds_next <= do_next:
                # Favor decreasing chebyshev distance to opponent (deterministic pressure).
                dself_opp = cheb(nx, ny, ox, oy)
                dob = cheb(sx, sy, ox, oy)
                block = (dself_opp - dob) * 0.05
            score = ds_next + 0.25 * near_obst(nx, ny) + block
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]
    else:
        # No resources: move toward opponent's corner with obstacle avoidance.
        tx, ty = (w - 1, h - 1) if (ox, oy) == (0, 0) else (0, 0)
        best_move = None
        best_score = None
        for dx, dy, nx, ny in legal:
            score = cheb(nx, ny, tx, ty) + 0.25 * near_obst(nx, ny)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]