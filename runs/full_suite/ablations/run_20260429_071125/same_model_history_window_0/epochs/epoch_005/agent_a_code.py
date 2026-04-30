def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    def sd2(px, py, qx, qy):
        dx = px - qx
        dy = py - qy
        return dx * dx + dy * dy

    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        # Choose the resource that maximizes "contested advantage": opponent distance minus our distance.
        best_adv = None
        best_self_d = None
        for rx, ry in resources:
            my_d = sd2(nx, ny, rx, ry)
            op_d = sd2(ox, oy, rx, ry)
            adv = op_d - my_d
            if best_adv is None or adv > best_adv or (adv == best_adv and my_d < best_self_d):
                best_adv = adv
                best_self_d = my_d
        # If we can secure a contested resource (positive advantage), prioritize it strongly.
        # Otherwise, still reduce distance to the best available resource.
        score = best_adv
        if best_adv is not None and best_adv > 0:
            score = score * 10 - best_self_d * 0.001
        else:
            score = (best_adv if best_adv is not None else -10**9) - best_self_d * 0.01
        if best_move is None or score > best_move[0]:
            best_move = (score, dx, dy, best_adv, best_self_d)

    if best_move is None:
        # Try staying out of obstacles: move minimally toward nearest resource.
        rx0, ry0 = min(resources, key=lambda p: sd2(sx, sy, p[0], p[1]))
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            d = sd2(nx, ny, rx0, ry0)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best else [0, 0]
    return [best_move[1], best_move[2]]