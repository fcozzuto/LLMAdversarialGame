def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    pursuer = ("pursuer" in role) and ("evader" not in role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        # small obstacle-avoidance term: count blocked neighboring cells
        blockn = 0
        for adx, ady in deltas:
            tx, ty = nx + adx, ny + ady
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in obs:
                blockn += 1
        if pursuer:
            key = (d, blockn, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        else:
            key = (-d, -blockn, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]