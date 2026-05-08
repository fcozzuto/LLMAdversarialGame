def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                obst.add((int(p[0]), int(p[1])))
            except Exception:
                pass

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    self_role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in self_role) or ("escape" in self_role)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = dist2(nx, ny, ox, oy)
        key = v if is_evader else -v
        if best is None or key > bestv:
            best, bestv = (dx, dy), key

    return [int(best[0]), int(best[1])]