def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = str(observation.get("self_role", "pursuer")).lower()
    maximize = (role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    obs_list = list(obs)

    def min_obs_dist2(x, y):
        m = None
        for ox2, oy2 in obs_list:
            d = dist2(x, y, ox2, oy2)
            if m is None or d < m:
                m = d
        return m if m is not None else 9999

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inb(nx, ny):
            continue
        d_now = dist2(nx, ny, int(ox), int(oy))
        mob = mobility(nx, ny)
        mo = min_obs_dist2(nx, ny)
        # Prefer staying away from obstacles when evading; prefer squeezing space when pursuing.
        if maximize:
            score = d_now * 10 + mob * 3 + mo * 0.01
        else:
            score = (-d_now) * 10 + mob * 1 + mo * 0.01
        if best_val is None or score > best_val:
            best_val = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]