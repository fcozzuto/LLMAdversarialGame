def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evader" in role) or ("runner" in role) or ("evading" in role)

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                res_list.append((rx, ry))

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    if res_list:
        target = min(res_list, key=lambda p: dist2(sx, sy, p[0], p[1]))
    else:
        target = (w // 2, h // 2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        toward = dist2(nx, ny, target[0], target[1])
        away = dist2(nx, ny, ox, oy)
        val = away - toward if i_am_evader else -away - toward
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]