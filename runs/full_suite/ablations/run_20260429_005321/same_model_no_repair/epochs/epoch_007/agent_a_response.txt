def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    # Prefer moves that maximize "reach advantage" to some resource
    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        best_r_key = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            can_take = 1 if sd <= od else 0
            swing = od - sd  # positive is better for us
            dist_pen = -sd
            tie = -(rx + 31 * ry)
            key = (can_take, swing, dist_pen, tie)
            if best_r_key is None or key > best_r_key:
                best_r_key = key
        if best_r_key is None:
            continue
        # Small preference to keep moving when tied
        move_key = (best_r_key, -(abs(nx - sx) + abs(ny - sy)))
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]