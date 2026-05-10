def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role") or "").lower()
    flee = ("evad" in sr) and ("purs" not in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        val = -d if flee else d  # flee: maximize distance => minimize negative distance
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    if safe(sx, sy):
        return best_move
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if safe(nx, ny):
            return [dx, dy]
    return [0, 0]