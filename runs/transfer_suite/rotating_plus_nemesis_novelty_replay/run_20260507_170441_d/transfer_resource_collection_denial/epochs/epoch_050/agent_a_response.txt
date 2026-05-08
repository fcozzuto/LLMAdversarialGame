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
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Target: prefer cells where we can arrive no later than opponent; break ties by larger slack vs opponent.
    best = None
    for rx, ry in resources:
        my_d = dist8(sx, sy, rx, ry)
        op_d = dist8(ox, oy, rx, ry)
        slack = op_d - my_d  # larger means we are relatively faster
        key = (-max(0, slack), my_d, -slack, rx, ry)  # maximize slack when possible; otherwise minimize my_d
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Move: consider all 8 neighbors + stay; choose deterministic best that reduces distance to target.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_d = dist8(sx, sy, tx, ty)
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = dist8(nx, ny, tx, ty)
        # Secondary: keep our next position as unfavorable as possible for opponent (increase their distance).
        op_nd = dist8(ox, oy, tx, ty)
        cand.append((nd - cur_d, nd, -op_nd, nx, ny, dx, dy))

    # If for some reason no move is valid (shouldn't), stay.
    if not cand:
        return [0, 0]

    cand.sort()
    return [cand[0][5], cand[0][6]]