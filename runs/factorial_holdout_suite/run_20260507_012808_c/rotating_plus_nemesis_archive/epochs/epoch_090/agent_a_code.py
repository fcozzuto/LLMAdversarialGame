def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Strategy: prefer a resource where we are closer than opponent; otherwise, pick the resource that we can become closer to soonest.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = dist2(sx, sy, rx, ry)
        od = dist2(ox, oy, rx, ry)
        # key: (win_flag, advantage, -my_dist) ; higher is better
        win_flag = 1 if sd < od else 0
        # smaller my_dist is better, so use negative
        key = (win_flag, od - sd, -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Obstacle-aware step: choose move that maximizes next-step target advantage; tie-break toward reducing distance.
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nsd = dist2(nx, ny, tx, ty)
        nod = dist2(ox, oy, tx, ty)
        key = (1 if nsd < nod else 0, nod - nsd, -nsd, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]