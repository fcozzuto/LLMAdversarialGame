def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obs = set()
    for p in (observation.get("obstacles") or []):
        if p is None or len(p) < 2:
            continue
        obs.add((int(p[0]), int(p[1])))
    resources = []
    for r in (observation.get("resources") or []):
        if r is None or len(r) < 2:
            continue
        resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def manh(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx + dy

    def obstacle_penalty(x, y):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    p += 1
        return p

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [-dx, -dy]

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        myd = []
        score_resource = -10**18
        for rx, ry in resources:
            md = manh((nx, ny), (rx, ry))
            od = manh((ox, oy), (rx, ry))
            # Prefer resources where we are closer; also prefer near-term collection.
            s = 2 * (od - md) - md
            if s > score_resource:
                score_resource = s
        if score_resource == -10**18:
            continue

        # Discourage paths that get too close to obstacles and chase opponent too hard.
        opp_adj = obstacle_penalty(nx, ny)
        opp_chase = -manh((nx, ny), (ox, oy)) * 0.02
        score = score_resource - 0.6 * opp_adj + opp_chase
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best