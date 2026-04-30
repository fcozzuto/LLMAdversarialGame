def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose target resource where we have the best relative advantage
    best = None
    best_key = None
    for rx, ry in resources:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        key = (od - sd, -(sd + 0.001 * (rx + ry)))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        # No resources: move toward center while not stepping onto obstacles (deterministic)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        target = (int(cx), int(cy))
    else:
        target = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer moves that get closer to our chosen target, but also avoid letting opponent take the next best advantage
        d_self = dist((nx, ny), target)
        d_opp = dist((ox, oy), target)
        # Look at whether this move improves our relative advantage to that target
        rel = (d_opp - d_self)
        # Secondary: keep a mild preference away from opponent to reduce contest
        d_oppenow = dist((nx, ny), (ox, oy))
        # Tie-break by deterministic ordering proxy (dx,dy)
        key = (rel, -d_self, d_oppenow, -abs(dx) - abs(dy))
        candidates.append((key, [dx, dy]))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]