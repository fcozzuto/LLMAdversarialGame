def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick a target we can reach earlier (or that gives best relative advantage).
    best = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        lead = op_d - my_d  # positive => we are better positioned
        key = (-lead, my_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry, my_d, op_d)
    _, tx, ty, _, _ = best

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        new_my_d = dist8(nx, ny, tx, ty)
        new_op_d = dist8(ox, oy, tx, ty)
        # Prefer: keep/improve relative advantage, then reduce own distance, then move toward corner-deterministically
        rel = new_op_d - new_my_d
        key = (-rel, new_my_d, nx, ny)
        candidates.append((key, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    return [candidates[0][1], candidates[0][2]]