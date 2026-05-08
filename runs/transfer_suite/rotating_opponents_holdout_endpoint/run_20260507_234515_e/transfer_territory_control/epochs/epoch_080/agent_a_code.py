def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    self_pos = observation.get("self_position") or [0, 0]
    opp_pos = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(self_pos[0]), int(self_pos[1])
    tx, ty = int(opp_pos[0]), int(opp_pos[1])

    obstacles_raw = observation.get("obstacles") or []
    obstacles = set()
    for o in obstacles_raw:
        try:
            ox, oy = o
            obstacles.add((int(ox), int(oy)))
        except:
            pass

    resources_raw = observation.get("resources") or []
    resources = []
    for r in resources_raw:
        try:
            rx, ry = r
            resources.append((int(rx), int(ry)))
        except:
            pass

    if resources:
        best = None
        for rx, ry in resources:
            d = abs(sx - rx) + abs(sy - ry)
            if best is None or d < best[0]:
                best = (d, rx, ry)
        _, tx, ty = best

    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    best_move = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        opp_dist = abs(nx - opp_pos[0]) + abs(ny - opp_pos[1])
        val = (dist, -opp_dist)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    if best_move is not None:
        return best_move
    return [0, 0]