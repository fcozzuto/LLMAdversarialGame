def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = str(observation.get("self_role") or "")
    evader = "evader" in role.lower()

    dlist = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    prev = None
    path = observation.get("self_path") or []
    if isinstance(path, list) and len(path) >= 2:
        p0, p1 = path[-2], path[-1]
        prev = (int(p1[0]) - int(p0[0]), int(p1[1]) - int(p0[1]))

    best_move = (0, 0)
    best_val = None

    for dx, dy in dlist:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked):
            continue
        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy
        val = dist2 if evader else -dist2
        if prev is not None and (dx, dy) == (-prev[0], -prev[1]):
            val -= 1
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]