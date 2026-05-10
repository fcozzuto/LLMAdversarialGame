def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # If opponent is using walls, aim one step inward to cut off the wall-running escape.
    inward_x = 0
    inward_y = 0
    if ox <= 0:
        inward_x = 1
    elif ox >= w - 1:
        inward_x = -1
    if oy <= 0:
        inward_y = 1
    elif oy >= h - 1:
        inward_y = -1

    tx = min(w - 1, max(0, ox + inward_x))
    ty = min(h - 1, max(0, oy + inward_y))
    if (inward_x == 0 and inward_y == 0) or (tx, ty) in obstacles:
        tx, ty = ox, oy

    best = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_target = dist2(nx, ny, tx, ty)
        d_opp = dist2(nx, ny, ox, oy)

        # Wall pressure: penalize being further to the open interior when opponent is on walls.
        wall_pen = 0
        if inward_x != 0 or inward_y != 0:
            # Prefer moving toward the grid center instead of sticking to the same edge.
            wall_pen = (abs((nx - (w - 1) / 2)) + abs((ny - (h - 1) / 2)))

        # Deterministic scoring and tie-breaking
        score = d_target * 10 + d_opp + wall_pen
        key = (score, d_target, d_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best