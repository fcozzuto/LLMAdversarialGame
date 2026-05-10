def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    candidates = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d = dist2((sx, sy), (rx, ry))
        candidates.append((d, rx, ry))
    candidates.sort()
    if candidates:
        _, tx, ty = candidates[0]
        # choose move that gets closer to (tx, ty) while not stepping onto obstacle
        best = (10**18, None, None)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if (nx, ny) in obstacles:
                    continue
                # keep within grid bounds
                if nx < 0 or nx >= w or ny < 0 or ny >= h:
                    continue
                nd = dist2((nx, ny), (tx, ty))
                # tie-break deterministically by preferring diagonal then axis then stay
                pref = 0
                if dx != 0 and dy != 0:
                    pref = 0
                elif dx == 0 and dy == 0:
                    pref = 2
                else:
                    pref = 1
                score = (nd, pref, nx, ny)
                if score < best[0:4]:
                    best = (nd, dx, dy)
        return [int(best[1]), int(best[2])]
    # no resources left: move to reduce distance to opponent as a deterministic fallback
    best = (10**18, 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obstacles:
                continue
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            nd = dist2((nx, ny), (ox, oy))
            score = (nd, nx, ny)
            if score < best[0:3]:
                best = (nd, dx, dy)
    return [int(best[1]), int(best[2])]