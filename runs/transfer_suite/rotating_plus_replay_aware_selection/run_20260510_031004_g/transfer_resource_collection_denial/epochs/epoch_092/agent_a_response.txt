def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Target selection: contest resources we can reach first; otherwise still head toward good races.
    best_r = None
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        key = (-(my_d > opp_d), opp_d - my_d, -my_d, rx, ry)  # prefer my_d<=opp_d, then larger lead
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    tx, ty = best_r

    # Move choice: try shortest step to target that doesn't hit an obstacle.
    candidates = []
    base_dx = 0 if tx == sx else (1 if tx > sx else -1)
    base_dy = 0 if ty == sy else (1 if ty > sy else -1)
    deltas = [[base_dx, base_dy], [base_dx, 0], [0, base_dy], [base_dx, -base_dy], [-base_dx, base_dy], [0, 0],
              [1, 1], [1, -1], [-1, 1], [-1, -1], [1, 0], [-1, 0], [0, 1], [0, -1]]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # Tie-break: also reduce chance opponent reaches earlier after our move.
        opp_after = cheb(ox, oy, tx, ty)
        candidates.append((d, opp_after - d, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(reverse=False)
    _, _, dx, dy = candidates[0]
    return [int(dx), int(dy)]