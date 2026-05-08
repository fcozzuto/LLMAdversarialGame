def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = str(observation.get("self_role") or "").lower()
    is_evader = "evad" in role

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    best_dxdy = [0, 0]
    best_key = None

    if is_evader:
        tx, ty = max(corners, key=lambda c: (dist2(c[0], c[1], ox, oy), c[0], c[1]))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            key = (dist2(nx, ny, ox, oy), -dist2(nx, ny, tx, ty), -dx, -dy)
            if best_key is None or key > best_key:
                best_key = key
                best_dxdy = [dx, dy]
    else:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            key = (-dist2(nx, ny, ox, oy), dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best_dxdy = [dx, dy]

    # Fallback if all moves blocked
    bx, by = sx, sy
    if (bx, by) in obstacles:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best_dxdy