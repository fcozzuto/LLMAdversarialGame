def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])

    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    options = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    viable = []
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            viable.append((dx, dy, nx, ny))
    if not viable:
        return [0, 0]

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            key = (do - ds, -ds)  # prefer resources we can reach sooner
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # no resources: drift away from opponent to reduce interception
        tx, ty = (sx - (1 if ox > sx else -1 if ox < sx else 0), sy - (1 if oy > sy else -1 if oy < sy else 0))
        tx = max(0, min(w - 1, tx))
        ty = max(0, min(h - 1, ty))

    best_move = None
    best_score = None
    for dx, dy, nx, ny in viable:
        my_d = dist(nx, ny, tx, ty)
        opp_d = dist(nx, ny, ox, oy)
        # prefer closer to target, penalize getting close to opponent
        score = (-my_d, opp_d)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]