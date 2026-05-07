def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_set = set(resources)

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = (None, -10**18)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Immediate capture priority
        if (nx, ny) in res_set:
            score = 10**9
        else:
            ds = 10**9
            do = 10**9
            # Compare how quickly we can get to a remaining resource vs opponent
            for rx, ry in resources:
                d1 = dist(nx, ny, rx, ry)
                if d1 < ds:
                    ds = d1
                d2 = dist(ox, oy, rx, ry)
                if d2 < do:
                    do = d2
            # Favor cells where we are closer than opponent, and generally reduce our distance
            score = (do - ds) * 1000 - ds

        # Mild preference to avoid being trapped by obstacles (prefer cells with more free neighbors)
        free_neighbors = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obstacles:
                free_neighbors += 1
        score += free_neighbors * 2

        if score > best[1]:
            best = ([dx, dy], score)

    return best[0] if best[0] is not None else [0, 0]