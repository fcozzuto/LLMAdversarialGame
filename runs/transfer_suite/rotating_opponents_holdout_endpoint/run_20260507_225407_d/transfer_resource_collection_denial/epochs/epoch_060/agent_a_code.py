def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w, h = int(observation.get("grid_width", 1)), int(observation.get("grid_height", 1))

    def norm_pos(p):
        try:
            x, y = p
            return int(x), int(y)
        except Exception:
            return None

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        t = norm_pos(p)
        if t and 0 <= t[0] < w and 0 <= t[1] < h:
            obs.add(t)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        t = norm_pos(p)
        if t and ok(t[0], t[1]):
            res.append(t)

    if not ok(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if ok(nx, ny):
                    return [dx, dy]
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if res:
            d1 = min(md((nx, ny), r) for r in res)
            d_op = md((nx, ny), (ox, oy))
            # Prefer getting closer to resources; slightly prefer being farther from opponent.
            key = (d1, -d_op, dx, dy)
        else:
            # No resources: move toward opponent to contest.
            key = (md((nx, ny), (ox, oy)), dx, dy)

        if best is None or key < best[0]:
            best = (key, (dx, dy))

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]