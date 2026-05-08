def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in sr) or ("pursue" in sr) or ("tagger" in sr) or ("chaser" in sr)
    if not sr:
        pursuer = True

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x, y, tx, ty):
        dx = x - tx
        dy = y - ty
        return dx * dx + dy * dy

    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist(nx, ny, ox, oy)
        v = -d if not pursuer else d
        if best is None or v > bestv:
            best = [dx, dy]
            bestv = v

    if best is None:
        return [0, 0]
    return best