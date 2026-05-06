def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Select the resource where we have the best "tempo" advantage (opp slower than us).
    best_res = None
    best_key = None
    for r in resources:
        ds = dist((sx, sy), r)
        do = dist((ox, oy), r)
        key = (-(do - ds), ds, r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best_res = r
    tx, ty = best_res

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    cur_ds = dist((sx, sy), (tx, ty))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        nds = dist((nx, ny), (tx, ty))
        # Approximate capture race at next step.
        self_race = (dist((ox, oy), (tx, ty)) - nds)

        # Small penalty for moving away from opponent directionally to reduce interference risk.
        opp_delta = abs((nx - ox) + (ny - oy))

        # If we can reduce distance, reward it strongly; otherwise be conservative.
        step_gain = cur_ds - nds
        score = (step_gain * 100) + (self_race * 10) - (opp_delta * 0.01) - (0.1 * (abs(dx) + abs(dy)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]