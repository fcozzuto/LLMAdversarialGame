def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    obs_set = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    srole = str(observation.get("self_role", "")).lower()
    orole = str(observation.get("opponent_role", "")).lower()
    pursuer = ("pursuer" in srole) or (("evader" in orole) and ("pursuer" not in srole))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    def score_move(nx, ny):
        d = dist2(nx, ny, ox, oy)
        m = mobility(nx, ny)
        # Small tie-breaks to ensure determinism and avoid oscillation
        tie = (nx + 3 * ny) - (sx + 3 * sy)
        if pursuer:
            return (-d, -m, tie)
        else:
            return (d, -m, -tie)

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = score_move(nx, ny)
        if best is None or sc > best:
            best = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]