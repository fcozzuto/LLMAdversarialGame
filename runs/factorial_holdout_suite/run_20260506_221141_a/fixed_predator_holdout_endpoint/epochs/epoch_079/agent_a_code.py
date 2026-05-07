def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if resources:
        best = None
        best_key = None  # (adv, -sd, -sumd) for max
        for rx, ry in resources:
            sd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = od - sd
            key = (adv, -sd, -(rx + ry))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)

        rx, ry = best
        target_dx = 0 if rx == sx else (1 if rx > sx else -1)
        target_dy = 0 if ry == sy else (1 if ry > sy else -1)

        candidates = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                gain = -md(nx, ny, rx, ry)
                align = - (abs(dx - target_dx) + abs(dy - target_dy))
                candidates.append((gain, align, (dx, dy)))
        if candidates:
            candidates.sort(reverse=True)
            return list(candidates[0][2])

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
    return [0, 0]