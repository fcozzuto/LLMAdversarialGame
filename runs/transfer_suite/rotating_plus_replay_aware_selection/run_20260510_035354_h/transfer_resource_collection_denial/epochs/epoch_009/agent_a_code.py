def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Prefer resources we can reach earlier (strictly), then minimize our arrival time.
    # If we can't beat any, head to the one that maximizes (their lead) denial by approaching their closest resource.
    best = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        diff = ds - do  # negative => we arrive first or tie-better depending on sign
        reach_gain = -diff  # bigger is better for us
        if diff <= 0:
            key = (0, -reach_gain, ds, do, rx, ry)
        else:
            # We are slower: pick what the opponent is closest to, while still making forward progress.
            key = (1, -do, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))

    tx, ty = best[1]
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    # Choose among 8-neighborhood + stay, avoiding obstacles. Deterministic tie-break by best distance-to-target.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (10**9, 10**9, 10**9)
    best_ret = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ns = dist(nx, ny, tx, ty)
        no = dist(nx, ny, ox, oy)
        # Also mildly prefer staying closer than the opponent to the target.
        opp_to_target = dist(ox, oy, tx, ty)
        score = (0 if ns <= opp_to_target else 1)
        key = (score, ns, -no, dx, dy)
        if key < best_move:
            best_move = key
            best_ret = [dx, dy]

    return best_ret if best_ret is not None else [0, 0]