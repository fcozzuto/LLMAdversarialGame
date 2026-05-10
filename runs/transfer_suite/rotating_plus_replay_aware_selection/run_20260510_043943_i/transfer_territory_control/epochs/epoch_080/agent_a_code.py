def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
    opp_pos = observation.get("opponent_position") or (sx, sy)
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if resources:
            dmin = min(man(nx, ny, rx, ry) for rx, ry in resources)
            score = -dmin
        else:
            score = -man(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is not None:
        return best

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            return [dx, dy]
    return [0, 0]