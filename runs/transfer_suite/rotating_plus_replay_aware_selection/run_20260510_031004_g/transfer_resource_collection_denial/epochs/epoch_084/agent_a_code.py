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

    # Prefer resources we can reach earlier; break ties by smaller own distance, then stable coord order.
    best = None
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        margin = opp_d - my_d  # positive => we likely arrive first
        key = (margin, -my_d, rx, ry)
        if best_key is None or key > best_key:
            best_key, best = key, (rx, ry)

    tx, ty = best

    steps = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    # Deterministic ordering: prefer moves that decrease distance to target.
    best_step = [0, 0]
    best_score = None
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # If opponent is closer to the target than we are, still move toward it but avoid losing too much tempo.
        cur_my_d = cheb(sx, sy, tx, ty)
        cur_opp_d = cheb(ox, oy, tx, ty)
        cur_margin = cur_opp_d - cur_my_d
        next_margin = cur_opp_d - d
        score = (next_margin, -d, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_score is None or score > best_score:
            best_score, best_step = score, [dx, dy]

    return best_step