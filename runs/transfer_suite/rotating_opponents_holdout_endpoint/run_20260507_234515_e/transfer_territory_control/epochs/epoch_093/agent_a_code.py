def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    unclaimed = []
    for c in observation.get("unclaimed_cells") or []:
        try:
            x, y = int(c[0]), int(c[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.append((x, y))
        except Exception:
            pass

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not unclaimed:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
        return [0, 0]

    target = None
    best = None
    for x, y in unclaimed:
        d = abs(x - sx) + abs(y - sy)
        if best is None or d < best or (d == best and (x, y) < target):
            best = d
            target = (x, y)

    tx, ty = target
    best_move = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = (abs(tx - nx) + abs(ty - ny), 0 if (nx, ny) in unclaimed else 1, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
        return [0, 0]

    return [int(best_move[0]), int(best_move[1])]