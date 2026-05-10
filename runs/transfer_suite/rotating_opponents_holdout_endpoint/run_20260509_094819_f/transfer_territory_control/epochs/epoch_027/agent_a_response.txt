def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    def to_set(v):
        s = set()
        for p in v or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set(observation.get("obstacles"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    selfT = to_set(observation.get("self_territory"))
    oppT = to_set(observation.get("opponent_territory"))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Candidate targets: prefer unclaimed, otherwise push into opponent territory; avoid stepping onto obstacles.
    targets = unclaimed if unclaimed else (oppT if oppT else set())
    if not targets:
        return [0, 0]

    best = None
    best_key = None
    for tx, ty in targets:
        if (tx, ty) in obstacles or (tx, ty) == (sx, sy):
            continue
        du = abs(tx - sx) + abs(ty - sy)
        do = abs(tx - ox) + abs(ty - oy)
        # Maximize safety (farther from opponent) and closeness
        key = (do - du, -du, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best

    # Choose a deterministic step that reduces distance to target while avoiding obstacles.
    # Tie-break: prefer staying within currently-controlled territory (slightly), then lexicographic.
    cur_d = max(abs(tx - sx), abs(ty - sy))
    best_move = (0, 0)
    best_score = None
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = max(abs(tx - nx), abs(ty - ny))
        gain = cur_d - nd
        in_ours = 1 if (nx, ny) in selfT else 0
        # If we're moving onto opponent territory, it's good (flipping enabled) unless it causes worse distance.
        in_theirs = 1 if (nx, ny) in oppT else 0
        score = (gain, in_ours, in_theirs, -abs(dx), -abs(dy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]