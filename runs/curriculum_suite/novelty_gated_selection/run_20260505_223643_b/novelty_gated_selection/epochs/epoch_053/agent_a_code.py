def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for item in observation.get("obstacles", []) or []:
        x = y = None
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            x, y = int(item[0]), int(item[1])
        elif isinstance(item, dict):
            if "x" in item and "y" in item:
                x, y = int(item["x"]), int(item["y"])
            else:
                p = item.get("position")
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
        if x is not None and 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for item in observation.get("resources", []) or []:
        x = y = None
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            x, y = int(item[0]), int(item[1])
        elif isinstance(item, dict):
            if "x" in item and "y" in item:
                x, y = int(item["x"]), int(item["y"])
            else:
                p = item.get("position")
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
        if x is not None and 0 <= x < w and 0 <= y < h:
            resources.append((x, y))

    target = None
    if resources:
        best = None
        for rx, ry in resources:
            d = abs(rx - sx) + abs(ry - sy)
            if best is None or d < best[0] or (d == best[0] and (ry, rx) < (best[2], best[1])):
                best = (d, rx, ry)
        target = (best[1], best[2])
    else:
        target = (ox, oy)

    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    best_move = (0, 0)
    best_score = None
    for dx in dxs:
        for dy in dys:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if target:
                tx, ty = target
                dist = abs(tx - nx) + abs(ty - ny)
            else:
                dist = 0
            score = -dist
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    if best_score is None:
        if inb(sx, sy):
            return [0, 0]
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny):
                    return [dx, dy]
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]