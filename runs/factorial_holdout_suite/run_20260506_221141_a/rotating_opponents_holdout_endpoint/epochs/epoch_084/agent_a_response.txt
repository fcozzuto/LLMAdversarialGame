def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb((sx, sy), (rx, ry))
        do = cheb((ox, oy), (rx, ry))
        lead = do - ds  # positive means we can arrive earlier
        can_win = 1 if lead >= 1 else 0
        # Prefer: guaranteed earlier, then larger lead, then smaller ds,
        # then deterministic coordinate tie-break.
        key = (can_win, lead, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = tx - sx
    dy = ty - sy
    if dx > 0:
        step_x = 1
    elif dx < 0:
        step_x = -1
    else:
        step_x = 0
    if dy > 0:
        step_y = 1
    elif dy < 0:
        step_y = -1
    else:
        step_y = 0

    return [step_x, step_y]