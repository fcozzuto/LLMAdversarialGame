def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def sign(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    tx, ty = None, None
    if resources:
        best = None
        for x, y in resources:
            d = max(abs(x - sx), abs(y - sy))
            if best is None or d < best[0]:
                best = (d, x, y)
        tx, ty = best[1], best[2]
    else:
        tx, ty = ox, oy

    dx0, dy0 = sign(tx - sx), sign(ty - sy)
    candidates = [(dx0, dy0), (dx0, 0), (0, dy0), (-dx0, dy0), (dy0, dx0), (0, 0)]
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]