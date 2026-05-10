def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w or 8)
        h = int(h or 8)
    except:
        w, h = 8, 8

    sp = observation.get("self_position") or [0, 0]
    try:
        sx, sy = int(sp[0]), int(sp[1])
    except:
        sx, sy = 0, 0

    op = observation.get("opponent_position") or [w - 1, h - 1]
    try:
        ox, oy = int(op[0]), int(op[1])
    except:
        ox, oy = w - 1, h - 1

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        try:
            obs.add((int(p[0]), int(p[1])))
        except:
            pass

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    for p in unclaimed:
        if p is None or len(p) < 2:
            continue
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            targets.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (0, 0, -10**9)
    found = False
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        if targets:
            tx, ty = min(targets, key=lambda t: (t[0]-nx)*(t[0]-nx) + (t[1]-ny)*(t[1]-ny))
            dist2 = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
            score = -dist2
        else:
            dist2 = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
            score = -dist2 // 2
            found = True
        if (nx, ny) == (ox, oy):
            score += 10**6
        if not found or score > best[2]:
            best = (dx, dy, score)
            found = True

    return [best[0], best[1]]