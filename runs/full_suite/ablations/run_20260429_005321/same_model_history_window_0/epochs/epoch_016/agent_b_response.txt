def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    def best_candidate_toward(tx, ty):
        candidates = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            candidates.append((dist2((nx, ny), (tx, ty)), dx, dy))
        if not candidates:
            return (0, 0)
        candidates.sort()
        return (candidates[0][1], candidates[0][2])

    if not resources:
        return [0, 0]

    # Pick a target that we can reach sooner than the opponent (or the best available).
    best = None
    for r in resources:
        rx, ry = r
        self_d = dist2((sx, sy), (rx, ry))
        opp_d = dist2((ox, oy), (rx, ry))
        score = (opp_d - self_d)  # higher means we are closer
        if best is None or score > best[0] or (score == best[0] and self_d < best[1]):
            best = (score, self_d, rx, ry)

    _, _, tx, ty = best
    dx, dy = best_candidate_toward(tx, ty)
    return [int(dx), int(dy)]