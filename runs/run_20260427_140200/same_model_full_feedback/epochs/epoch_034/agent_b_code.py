def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    spx, spy = int(sp[0]), int(sp[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        tx, ty = w // 2, h // 2
        dx = -1 if spx > tx else (1 if spx < tx else 0)
        dy = -1 if spy > ty else (1 if spy < ty else 0)
        if dx == 0 and dy == 0:
            return [0, 0]
        if dx != 0:
            nx, ny = spx + dx, spy
            if 0 <= nx < w and (nx, ny) not in obstacles:
                return [dx, 0]
        ny = spy + dy
        if 0 <= ny < h and (spx, ny) not in obstacles:
            return [0, dy]
        return [0, 0]

    def md(x, y, r):
        return abs(x - r[0]) + abs(y - r[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = spx + dx, spy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dmin = min(md(nx, ny, r) for r in resources)
        score = (dmin, abs(nx - (w // 2)) + abs(ny - (h // 2)))
        if best is None or score < best[0]:
            best = (score, [dx, dy])
    if best is None:
        return [0, 0]
    return best[1]