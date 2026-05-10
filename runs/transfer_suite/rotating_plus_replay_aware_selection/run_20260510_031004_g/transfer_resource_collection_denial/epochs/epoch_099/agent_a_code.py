def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    rem = observation.get("remaining_resource_count", len(resources))
    rem = int(rem) if isinstance(rem, int) or (isinstance(rem, float) and rem == int(rem)) else len(resources)

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; if tied, prefer ones closer and less "easy" for opponent.
        reach_adv = opp_d - my_d
        dist_pref = -my_d
        opp_pressure = -opp_d
        # Slightly favor further-away targets when resources are plentiful (avoid local myopia).
        far_bias = man(sx, sy, rx, ry) if rem > 6 else -man(sx, sy, rx, ry)
        key = (reach_adv, dist_pref, far_bias, opp_pressure, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    step_x = 0
    if tx > sx: step_x = 1
    elif tx < sx: step_x = -1
    step_y = 0
    if ty > sy: step_y = 1
    elif ty < sy: step_y = -1

    # If the direct diagonal target square is blocked, try axis-aligned alternatives deterministically.
    nx, ny = sx + step_x, sy + step_y
    if (step_x != 0 or step_y != 0) and (nx, ny) in obstacles:
        cand = []
        if step_x != 0:
            cand.append((step_x, 0))
        if step_y != 0:
            cand.append((0, step_y))
        cand.append((0, 0))
        for dx, dy in cand:
            fx, fy = sx + dx, sy + dy
            if 0 <= fx < w and 0 <= fy < h and (fx, fy) not in obstacles:
                return [int(dx), int(dy)]
        return [0, 0]

    if 0 <= sx + step_x < w and 0 <= sy + step_y < h:
        return [int(step_x), int(step_y)]
    return [0, 0]