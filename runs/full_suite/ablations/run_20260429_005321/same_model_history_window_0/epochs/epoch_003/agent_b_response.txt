def choose_move(observation):
    x0, y0 = observation["self_position"]
    ox0, oy0 = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_r = None
    best_val = None
    for r in resources:
        r = (r[0], r[1])
        if r in obstacles:
            continue
        sd = dist((x0, y0), r)
        od = dist((ox0, oy0), r)
        # Prefer resources that opponent is farther from; slight preference for being closer.
        val = (od - sd) * 10 - sd
        if best_val is None or val > best_val or (val == best_val and sd < dist((x0, y0), best_r)):
            best_val = val
            best_r = r

    tx, ty = best_r
    self_dist_now = dist((x0, y0), best_r)
    opp_dist_now = dist((ox0, oy0), best_r)

    candidates = []
    for dx, dy in moves:
        nx, ny = x0 + dx, y0 + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        sd = dist((nx, ny), best_r)
        od = dist((ox0, oy0), best_r)
        # Primary: reduce distance to target; Secondary: keep advantage over opponent.
        score = (opp_dist_now - sd) * 100 - sd
        # Deterministic tie-break favoring progress and consistency
        candidates.append((score, sd, abs(dx) + abs(dy), dx, dy, nx, ny))
    candidates.sort(reverse=True)
    if not candidates:
        return [0, 0]
    return [int(candidates[0][3]), int(candidates[0][4])]