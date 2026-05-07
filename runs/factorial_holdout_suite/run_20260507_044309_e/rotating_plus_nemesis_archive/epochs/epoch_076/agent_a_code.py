def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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
            if 0 <= rx < w and 0 <= ry < h:
                resources.append((rx, ry))

    def man(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx + dy

    def obst_penalty(px, py, tx, ty):
        dx = 1 if tx > px else (-1 if tx < px else 0)
        dy = 1 if ty > py else (-1 if ty < py else 0)
        x, y = px, py
        pen = 0
        steps = man((px, py), (tx, ty))
        for _ in range(steps):
            if x == tx and y == ty:
                break
            nx = x + dx
            ny = y + dy
            if (nx, ny) in obstacles:
                pen += 3
            x, y = nx, ny
            if x < 0 or x >= w or y < 0 or y >= h:
                break
        return pen

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        our_d = man((sx, sy), (rx, ry)) + obst_penalty(sx, sy, rx, ry)
        opp_d = man((ox, oy), (rx, ry)) + obst_penalty(ox, oy, rx, ry)
        # Prefer cells we reach earlier; if close, prefer one with larger opponent disadvantage.
        key = (our_d - opp_d, our_d, -rx, -ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_step = [0, 0]
    best_step_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        our_after = man((nx, ny), (tx, ty))
        opp_after = man((ox, oy), (tx, ty))
        # Keep moving toward target; tie-break by reducing our distance more.
        step_key = (our_after, (our_after - opp_after), -nx, -ny)
        if best_step_key is None or step_key < best_step_key:
            best_step_key = step_key
            best_step = [dx, dy]
    return best_step