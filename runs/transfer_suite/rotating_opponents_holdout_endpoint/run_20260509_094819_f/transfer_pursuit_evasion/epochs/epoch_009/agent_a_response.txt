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
    is_evader = "evad" in self_role

    cx, cy = (w - 1) * 0.5, (h - 1) * 0.5
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    def dist2(nx, ny, ax, ay):
        dx = nx - ax
        dy = ny - ay
        return dx * dx + dy * dy

    best_key = None
    best = (0, 0)

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        center_pen = dist2(nx, ny, cx, cy)
        # Key ordering: smaller is better.
        if is_evader:
            key = (-d, center_pen)  # maximize distance, but avoid extreme corners
        else:
            key = (d, center_pen)   # minimize distance; tie-break toward center
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]