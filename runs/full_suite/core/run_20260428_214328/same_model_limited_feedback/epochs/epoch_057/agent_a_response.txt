def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Choose best resource: prefer ones we can reach sooner than opponent
    best = None
    best_key = None
    for r in resources:
        r = tuple(r)
        if r in obstacles:
            continue
        sd = dist2((x, y), r)
        od = dist2((ox, oy), r)
        key = (od - sd, -sd)  # maximize advantage, then minimize our distance
        if best is None or key > best_key:
            best = r
            best_key = key

    if best is None:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        target = (int(round(tx)), int(round(ty)))
    else:
        target = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist2((nx, ny), target)
        # Additional heuristic: avoid stepping into cells adjacent to many obstacles
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if 0 <= px < w and 0 <= py < h and (px, py) in obstacles:
                    adj += 1
        # If target is contested, slightly prefer moves that increase distance from opponent
        od = dist2((nx, ny), (ox, oy))
        contested = 1 if best is not None else 0
        score = (-d, adj, -od * contested)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]