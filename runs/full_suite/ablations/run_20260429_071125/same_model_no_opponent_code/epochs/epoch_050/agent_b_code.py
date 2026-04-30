def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if resources:
        best_r = None
        best_d = 10**9
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            if d < best_d:
                best_d = d
                best_r = (rx, ry)
        rx, ry = best_r
        best = None
        for dx, dy, nx, ny in valid:
            score = (abs(rx - nx) + abs(ry - ny))
            opp = abs(ox - nx) + abs(oy - ny)
            key = (score, -opp, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1]

    best = None
    for dx, dy, nx, ny in valid:
        score = -(abs(ox - nx) + abs(oy - ny))
        key = (score, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]