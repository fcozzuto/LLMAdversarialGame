def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources_raw = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []

    if not (isinstance(sx, int) and isinstance(sy, int) and 0 <= sx < w and 0 <= sy < h):
        return [0, 0]
    if not (isinstance(ox, int) and isinstance(oy, int) and 0 <= ox < w and 0 <= oy < h):
        ox, oy = 0, 0

    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in resources_raw:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    tx, ty = min(resources, key=lambda t: (dist(sx, sy, t[0], t[1]), t[0], t[1]))
    dx = 0 if sx == tx else (1 if tx > sx else -1)
    dy = 0 if sy == ty else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    seen = set()
    for mx, my in candidates:
        if (mx, my) in seen:
            continue
        seen.add((mx, my))
        nx, ny = sx + mx, sy + my
        if not (isinstance(mx, int) and isinstance(my, int) and mx in (-1, 0, 1) and my in (-1, 0, 1)):
            continue
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [mx, my]

    return [0, 0]