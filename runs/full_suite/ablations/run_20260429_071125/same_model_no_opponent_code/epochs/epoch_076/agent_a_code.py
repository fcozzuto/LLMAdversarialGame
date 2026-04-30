def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    targets = resources
    best_t = None
    best_t_score = -10**18
    if targets:
        for tx, ty in targets:
            my_d = cheb(sx, sy, tx, ty)
            op_d = cheb(ox, oy, tx, ty)
            center_bias = -0.15 * cheb(tx, ty, (w - 1) // 2, (h - 1) // 2)
            block_bias = 0.0
            if (tx, ty) in obstacles:
                block_bias = -1e9
            score = (op_d - my_d) * 2.0 + center_bias + block_bias
            if score > best_t_score:
                best_t_score = score
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d2 = cheb(nx, ny, tx, ty)
        op_d2 = cheb(nx, ny, ox, oy)
        opp_to_target = cheb(ox, oy, tx, ty)
        my_to_target_now = cheb(sx, sy, tx, ty)
        improve = (my_to_target_now - my_d2)
        obstacle_pen = 0
        # small penalty if next to obstacle to avoid awkward slips
        for ax, ay in obstacles:
            if cheb(nx, ny, ax, ay) == 1:
                obstacle_pen -= 0.25
        val = improve * 2.5 - my_d2 + (op_d2 * 0.15) - (opp_to_target * 0.02) + obstacle_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if int(dx) not in (-1, 0, 1) or int(dy) not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]