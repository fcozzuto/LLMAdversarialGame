def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        try:
            x, y = p
            obst.add((int(x), int(y)))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    best = None
    best_score = None
    for dx, dy, nx, ny in cand:
        if resources:
            mine = 10**9
            theirs = 10**9
            for r in resources:
                try:
                    rx, ry = r
                    rx, ry = int(rx), int(ry)
                except:
                    continue
                dm = dist(nx, ny, rx, ry)
                dt = dist(ox, oy, rx, ry)
                if dm < mine: mine = dm
                if dt < theirs: theirs = dt
            score = (mine - theirs, mine, (dx == 0 and dy == 0))
        else:
            score = (0, 0, (dx == 0 and dy == 0))
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]