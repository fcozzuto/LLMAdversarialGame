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

    best = (None, None)  # (key, move)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        best_r = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # primary: can arrive no later than opponent
            can_take = 1 if sd <= od else 0
            # if both can take/compete, prefer bigger arrival advantage for us
            swing = (od - sd)  # positive if we are closer
            # tie-break: prefer smaller sd and more "toward our side" target bias
            dist_pen = -sd
            bias = -(rx + 7 * ry)  # deterministic bias
            key = (can_take, swing, dist_pen, bias)
            if best_r is None or key > best_r:
                best_r = key

        if best_r is None:
            continue

        # If same resource preference, slightly prefer moves that progress (not staying still unless best)
        prog = -(abs(nx - sx) + abs(ny - sy))
        move_key = (best_r, prog)
        if best[0] is None or move_key > best[0]:
            best = (move_key, (dx, dy))

    if best[1] is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]