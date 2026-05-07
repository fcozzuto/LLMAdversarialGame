def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        # Drift toward center while avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                val = -(cheb(nx, ny, cx, cy))
                if best is None or val > best[0]:
                    best = (val, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best_val = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate best reachable resource from this candidate position
        best_res_val = None
        for tx, ty in resources:
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Lead-first: favor actions that increase (opponent distance - our distance)
            # Secondary: prefer closer to us; tertiary: prefer breaking ties toward opponent
            lead = od - sd
            res_val = (lead, -sd, -od, tx, ty)
            if best_res_val is None or res_val > best_res_val:
                best_res_val = res_val
        if best_res_val is None:
            continue

        # Slightly prefer not to move if equally good (reduces oscillations)
        move_cost = 0 if (dx == 0 and dy == 0) else 1
        overall = (best_res_val[0], best_res_val[1], -move_cost, best_res_val[3], best_res_val[4])
        if best_val is None or overall > best_val:
            best_val = overall
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]