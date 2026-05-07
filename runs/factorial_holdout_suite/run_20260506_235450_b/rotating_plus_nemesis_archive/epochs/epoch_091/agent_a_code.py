def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    move_order = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_move = (-(10**9), 10**9, 10**9)
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        best_urg = -10**9
        best_sd = 10**9
        best_sum = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            urg = od - sd  # positive => closer than opponent
            if urg > best_urg or (urg == best_urg and (sd < best_sd or (sd == best_sd and (sd + od) < best_sum))):
                best_urg, best_sd, best_sum = urg, sd, sd + od

        move_score = (best_urg, -best_sd, -best_sum)
        if move_score > best_move:
            best_move = move_score
            ret = [dx, dy]

    return ret