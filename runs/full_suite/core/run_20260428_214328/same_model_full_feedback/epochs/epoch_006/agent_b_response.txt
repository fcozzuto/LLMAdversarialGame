def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if res:
        best = None
        best_key = None
        for rx, ry in res:
            sd = manh(sx, sy, rx, ry)
            od = manh(ox, oy, rx, ry)
            adv = od - sd  # positive means we're closer than opponent
            key = (-adv, sd, rx, ry)  # maximize adv; then minimize sd
            if best is None or key < best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
    else:
        tx, ty = ox, oy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        d_to_t = manh(nx, ny, tx, ty)
        opp_d = manh(ox, oy, tx, ty)

        # primary: get closer to target; secondary: reduce opponent's relative progress by threatening same target
        val = -d_to_t * 10 - d_to_t
        val += (opp_d - manh(nx, ny, tx, ty)) * 3

        # mild: keep away from opponent unless it helps reach target
        opp_dist = manh(nx, ny, ox, oy)
        val += opp_dist * 0.2

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]