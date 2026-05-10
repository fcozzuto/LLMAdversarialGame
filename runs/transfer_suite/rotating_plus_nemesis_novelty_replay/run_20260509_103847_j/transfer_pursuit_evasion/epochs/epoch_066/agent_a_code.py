def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = observation.get("obstacles") or []
    blocked = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if (sx, sy) == (ox, oy):
        return [0, 0]

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("evade" in role) or ("runner" in role)

    tx = ox - sx
    ty = oy - sy
    dx1 = 1 if tx > 0 else -1 if tx < 0 else 0
    dy1 = 1 if ty > 0 else -1 if ty < 0 else 0
    if is_evader:
        dx1, dy1 = -dx1, -dy1

    candidates = [(dx1, dy1), (dx1, 0), (0, dy1), (-dx1, dy1), (dx1, -dy1), (-dx1, 0), (0, -dy1), (0, 0)]
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]