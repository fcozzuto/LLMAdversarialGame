def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = str(observation.get("self_role", "pursuer")).lower()
    is_evader = (role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    obs_list = list(obs)

    def min_obs_d2(x, y):
        m = 10**9
        for a, b in obs_list:
            d = dist2(x, y, a, b)
            if d < m:
                m = d
        return m if obs_list else 10**9

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    best = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inb(nx, ny):
            continue
        d2 = dist2(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        mo = min_obs_d2(nx, ny)

        if is_evader:
            val = (-d2) + 0.06 * mob - 0.002 * (1.0 * d2 if mo == 0 else 0.0) + 0.0005 * mo
        else:
            val = (d2) - 0.04 * mob - 0.0005 * mo

        # Prefer lower val for pursuer, higher val for evader; deterministic tie-break by (dx,dy)
        if best_val is None:
            best_val, best = val, [dx, dy]
        else:
            better = (val < best_val) if not is_evader else (val > best_val)
            if better or (val == best_val and (dx, dy) < (best[0], best[1])):
                best_val, best = val, [dx, dy]

    return best