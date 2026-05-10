def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0)) % 9
    dirs = dirs[t:] + dirs[:t]

    scores = observation.get("scores") or {}
    self_name = observation["self_name"]
    opp_name = observation["opponent_name"]
    self_score = float(scores.get(self_name, 0.0)) if isinstance(scores, dict) else 0.0
    opp_score = float(scores.get(opp_name, 0.0)) if isinstance(scores, dict) else 0.0

    need_recover = (int(observation.get("self_territory_count", 0)) < int(observation.get("opponent_territory_count", 0))) or (self_score <= opp_score)
    candidates = list(unclaimed) if need_recover else list(opp_terr) if opp_terr else list(unclaimed)
    if not candidates:
        candidates = list(opp_terr) if opp_terr else list(self_terr)
    if not candidates:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target deterministically: best (min distance, tie by y then x)
    best_target = None
    best_key = None
    for p in candidates:
        k = (dist((sx, sy), p), p[1], p[0])
        if best_key is None or k < best_key:
            best_key = k
            best_target = p

    tx, ty = best_target

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        # Heuristic: prefer capturing/collaring cells and reducing distance to target.
        gain = 0
        if cell in unclaimed:
            gain += 4
        if cell in opp_terr:
            gain += 6
        if cell in self_terr:
            gain += 1

        # Slightly penalize stepping onto opponent territory if we are far behind, to stabilize; otherwise attack.
        if (not need_recover) and (cell in opp_terr):
            gain += 2
        if need_recover and (cell in opp_terr):
            gain -= 1

        d = abs(nx - tx) + abs(ny - ty)
        # Prefer not moving if equally good to reduce risk of obstacle collisions.
        move_pen = 0 if (dx == 0 and dy == 0) else 0.1
        val = -(gain * 10) + d + move_pen

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]