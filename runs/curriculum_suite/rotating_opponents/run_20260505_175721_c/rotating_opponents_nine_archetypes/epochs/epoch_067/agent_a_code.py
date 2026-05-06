def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    cx, cy = w // 2, h // 2
    ds_center = man(sx, sy, cx, cy)
    do_center = man(ox, oy, cx, cy)
    center_priority = 1 if ds_center > do_center else 0  # if opponent is closer to center, don't mirror; if we are closer, take center

    best = None
    best_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Favor advantage, but still choose a reachable target
        adv = od - sd  # positive means we are closer
        key = (0, -adv, sd, rx, ry) if center_priority == 0 else (1, -adv, man(rx, ry, cx, cy), sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    if center_priority == 1 and man(sx, sy, cx, cy) <= sd + 1:
        tx, ty = cx, cy

    step_options = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    def cell_ok(dx, dy):
        nx, ny = sx + dx, sy + dy
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    for dx, dy in [(desired_dx, desired_dy), (desired_dx, 0), (0, desired_dy), (0, 0)]:
        if cell_ok(dx, dy):
            return [int(dx), int(dy)]

    for dx, dy in step_options:
        if cell_ok(dx, dy):
            return [int(dx), int(dy)]

    return [0, 0]