def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    pursuer = ("pursuer" in role) or ("player" in role and "evader" not in role)

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    cx, cy = w // 2, h // 2
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if res:
        tx, ty = min(res, key=lambda p: dist2(sx, sy, p[0], p[1]))
    else:
        tx, ty = cx, cy if pursuer else (ox, oy)

    def objective(nx, ny):
        dtx = dist2(nx, ny, tx, ty)
        dto = dist2(nx, ny, ox, oy)
        if pursuer:
            return dtx - 0.01 * dto
        return dtx + 0.01 * dto

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = objective(nx, ny)
        key = (val, dx, dy)
        if best is None or key < best_val:
            best = [dx, dy]
            best_val = key
    if best is None:
        return [0, 0]
    return best