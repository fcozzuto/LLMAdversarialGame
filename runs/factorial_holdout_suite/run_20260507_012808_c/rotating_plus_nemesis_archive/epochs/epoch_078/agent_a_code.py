def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]
    if not resources:
        return [0, 0]

    def mdist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    best = None
    for dx, dy, nx, ny in candidates:
        # If we can grab a resource now, prioritize deterministically
        now = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                now = 1
                break
        if now:
            val = (1, -mdist((nx, ny), (ox, oy)), -nx, -ny, dx, dy)
        else:
            # Choose the resource that gives maximum "beat" margin (opp_dist - self_dist)
            best_adv = -10**18
            best_self_d = 10**18
            for rx, ry in resources:
                self_d = mdist((nx, ny), (rx, ry))
                opp_d = mdist((ox, oy), (rx, ry))
                adv = opp_d - self_d
                if adv > best_adv or (adv == best_adv and (self_d < best_self_d or (self_d == best_self_d and (rx, ry) < resources[0]))):
                    best_adv = adv
                    best_self_d = self_d
            # Prefer higher beat margin; if tied, prefer closer to that target and then lexicographically stable tie-break
            val = (0, best_adv, -best_self_d, -nx, -ny, dx, dy)
        if best is None or val > best:
            best = val

    return [best[-2], best[-1]]