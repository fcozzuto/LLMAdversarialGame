def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def md(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    my_half_right = (sx <= w // 2)
    if (ox <= w // 2) == my_half_right:
        my_half_right = not my_half_right

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    best_val = -10**18

    # Evaluate each immediate move by its best "take-the-advantage" resource.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Small deterministic obstacle avoidance: penalize staying if a neighbor cell is blocked
        block_pen = 0
        for ox1, oy1 in ((1,0),(-1,0),(0,1),(0,-1)):
            tx, ty = sx + ox1, sy + oy1
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obstacles:
                block_pen += 1
        block_pen = -0.02 * block_pen if (nx, ny) == (sx, sy) else 0

        # Choose the most favorable resource after this move.
        step_best = -10**18
        for rx, ry in resources:
            self_d = md((nx, ny), (rx, ry))
            opp_d = md((ox, oy), (rx, ry))
            margin = opp_d - self_d  # positive means we are closer/at least not worse
            # Bias: prefer resources on our side and those closer overall.
            side_bias = 0.15 if (rx >= w//2) == my_half_right else 0.0
            closeness = -0.02 * self_d
            # If we can grab quickly, prioritize strongly.
            quick = 0.35 if self_d <= 1 else 0.0
            val = margin + side_bias + closeness + quick
            if val > step_best:
                step_best = val

        # Also mildly prefer progressing toward the opponent's corner.
        toward_opp = md((nx, ny), (ox, oy))
        prog = -0.01 * toward_opp
        val_total = step_best + block_pen + prog

        if val_total > best_val:
            best_val = val_total
            best = [dx, dy]

    return best