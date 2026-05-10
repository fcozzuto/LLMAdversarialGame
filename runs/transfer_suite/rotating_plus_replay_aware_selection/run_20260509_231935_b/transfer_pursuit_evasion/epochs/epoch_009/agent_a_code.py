def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            obs.add((int(x), int(y)))
        except:
            pass

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in sr) and not ("evad" in orr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def mobility(x, y):
        seen = {(x, y)}
        frontier = [(x, y)]
        steps = 0
        count = 0
        while frontier and steps < 2:
            nxt = []
            for cx, cy in frontier:
                count += 1
                for dx, dy in deltas:
                    nx, ny = cx + dx, cy + dy
                    if in_bounds(nx, ny) and (nx, ny) not in obs and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        nxt.append((nx, ny))
            frontier = nxt
            steps += 1
        return count

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    best_dx, best_dy = 0, 0
    best_s = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue
        md = abs(nx - ox) + abs(ny - oy)
        mob = mobility(nx, ny)

        if self_is_evader:
            corner_dist = min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)
            # Evade: prioritize distance and freedom; avoid getting too close to any corner (escape routes).
            s = md + 0.15 * mob - 0.03 * corner_dist
        else:
            # Pursue: minimize distance; prefer moves that keep options open.
            s = -md + 0.06 * mob

        if best_s is None or s > best_s:
            best_s = s
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]