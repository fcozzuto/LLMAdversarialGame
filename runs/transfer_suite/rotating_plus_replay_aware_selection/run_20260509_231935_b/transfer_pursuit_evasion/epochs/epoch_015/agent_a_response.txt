def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obs_set.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in sr) and ("evad" not in orr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    order = {d: i for i, d in enumerate(deltas)}

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def mobility(x, y):
        cnt = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs_set:
                cnt += 1
        return cnt

    def walliness(x, y):
        adj = 0
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obs_set:
                adj += 1
        return adj

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        d = dist(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        wall = walliness(nx, ny)

        # Deterministic tie-break: prefer earlier in deltas order.
        if self_is_evader:
            # Evader: maximize distance, keep mobility high, avoid being pressed against obstacles.
            val = (d * 10.0) + (mob * 1.5) - (wall * 1.0)
        else:
            # Pursuer: minimize distance, increase mobility to avoid dead-ends.
            val = (-d * 10.0) + (mob * 1.2) - (wall * 0.8)

        if best_val is None or val > best_val or (val == best_val and order[(dx, dy)] < order[best]):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]