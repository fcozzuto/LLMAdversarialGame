def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("runner" in r) or ("evasion" in r) or ("evasive" in r)

    evading = is_evader(observation.get("self_role"))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    obs_list = list(obstacles) if obstacles else []
    def min_obst_d2(x, y):
        if not obs_list:
            return 999999
        best = 999999
        for bx, by in obs_list:
            d = dist2(x, y, bx, by)
            if d < best:
                best = d
        return best

    def score(nx, ny, dx, dy):
        d = dist2(nx, ny, ox, oy)
        # pursuer: minimize distance; evader: maximize distance
        s = d if evading else -d
        # avoid obstacles proximity; also avoid standing if it doesn't help
        md = min_obst_d2(nx, ny)
        s += (md < 5) * (50 - 10 * md)
        s += (dx == 0 and dy == 0) * (30 if (dist2(sx, sy, ox, oy) >= d if not evading else dist2(sx, sy, ox, oy) <= d) else 0)
        # slight preference for progressing (break ties deterministically)
        s += (abs(dx) + abs(dy) == 2) * (-0.5 if not evading else 0.5)
        return s

    best = None
    best_s = None
    tie = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        s = score(nx, ny, dx, dy)
        if best_s is None or s < best_s or (s == best_s and (dx, dy) < tie):
            best_s = s
            best = (dx, dy)
            tie = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]