def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []
    targets = []
    for lst in (resources, unclaimed):
        for p in lst:
            if len(targets) >= 60:
                break
            try:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                    targets.append((x, y))
            except:
                pass
        if len(targets) >= 60:
            break

    def md(a, b, c, d):
        ax = a - c
        if ax < 0:
            ax = -ax
        ay = b - d
        if ay < 0:
            ay = -ay
        return ax + ay

    if targets:
        tx, ty = targets[0]
        bestd = md(sx, sy, tx, ty)
        for x, y in targets[1:]:
            d = md(sx, sy, x, y)
            if d < bestd:
                bestd = d
                tx, ty = x, y
    else:
        tx, ty = ox, oy

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        dist = md(nx, ny, tx, ty)
        score = -dist
        score += -0.15 * md(nx, ny, ox, oy)  # mildly avoid opponent proximity
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move