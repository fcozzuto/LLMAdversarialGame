def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    blocked = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    evade = ("evad" in self_role) or ("purs" in opponent_role and "evad" in self_role)

    order = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    best = None
    best_key = None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in order:
        nx, ny = x + dx, y + dy
        if not ok(nx, ny):
            continue
        d = dist2((nx, ny), (ox, oy))
        center_pen = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        key = (d if not evade else -d, -center_pen)  # smaller is better for pursue
        if best is None or key < best_key:
            best = (dx, dy)
            best_key = key

    if best is None:
        best = (0, 0)
        if ok(x, y):
            return [0, 0]
        for dx, dy in order:
            if ok(x + dx, y + dy):
                return [dx, dy]
        return [0, 0]

    return [best[0], best[1]]