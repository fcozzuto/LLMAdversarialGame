def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    sr = str(observation.get("self_role", "")).lower()
    evader = ("evad" in sr) or ("escape" in sr) or ("runner" in sr)

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(nx, ny):
        if (nx, ny) in obs:
            return -10**9
        if res:
            best = 10**18
            for x, y in res:
                d = (nx - x) * (nx - x) + (ny - y) * (ny - y)
                if d < best:
                    best = d
            if evader:
                # Prefer distancing from opponent while still moving toward a resource.
                return -((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)) - best * 0.01
            return -best + (((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)) * 0.0005)
        # No resources: chase or flee.
        d2o = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        return d2o if evader else -d2o

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = score_cell(nx, ny)
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]
    return best_move