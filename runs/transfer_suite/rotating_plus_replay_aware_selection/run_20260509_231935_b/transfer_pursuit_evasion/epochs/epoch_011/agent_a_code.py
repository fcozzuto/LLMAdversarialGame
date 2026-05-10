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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def mobility(x, y):
        seen = {(x, y)}
        frontier = [(x, y)]
        for _ in range(2):
            nxt = []
            for cx, cy in frontier:
                for dx, dy in deltas:
                    nx, ny = cx + dx, cy + dy
                    if in_bounds(nx, ny) and (nx, ny) not in obs_set and (nx, ny) not in seen:
                        seen.add((nx, ny))
                        nxt.append((nx, ny))
            frontier = nxt
            if not frontier:
                break
        return len(seen)

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue
        md = abs(nx - ox) + abs(ny - oy)
        mob = mobility(nx, ny)
        if self_is_evader:
            val = (md * 1000) + (mob * 3) - ((nx == ox and ny == oy) * 1000000)
        else:
            val = (-md * 1000) + (mob * 1) - ((nx == ox and ny == oy) * 1000000)
        if best is None:
            best, best_val = (dx, dy), val
        else:
            if val > best_val or (val == best_val and (dx, dy) < best):
                best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]