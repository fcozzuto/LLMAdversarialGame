def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        x = y = None
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
        elif isinstance(t, dict):
            p = t.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
            else:
                x, y = int(t.get("x", -1)), int(t.get("y", -1))
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for t in observation.get("resources") or []:
        x = y = None
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
        elif isinstance(t, dict):
            p = t.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
            else:
                x, y = int(t.get("x", -1)), int(t.get("y", -1))
        if x is not None and y is not None and 0 <= x < w and 0 <= y < h:
            resources.append((x, y))

    def dist(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
    best = (None, -10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        score = 0
        if resources:
            md = 10**9
            for rx, ry in resources:
                d = dist(nx, ny, rx, ry)
                if d < md:
                    md = d
            score += 1000 - 10 * md
        score += -dist(nx, ny, ox, oy) * 2
        if (nx, ny) in resources:
            score += 5000
        if dx == 1 and dy == 0:
            score += 1  # deterministic tie-break favor
        elif dx == -1 and dy == 0:
            score += 0
        elif dx == 0 and dy == -1:
            score += 0
        elif dx == 0 and dy == 1:
            score += 0

        if score > best[1]:
            best = ([dx, dy], score)

    if best[0] is None:
        return [0, 0]
    return best[0]