def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("runner" in role) or ("evading" in role)

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obstacle_clearance(x, y):
        if not obstacles:
            return 99
        best = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        return best if best != 10**9 else 99

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d = manhattan(nx, ny, ox, oy)
        c = obstacle_clearance(nx, ny)

        # Deterministic tie-break: prefer keeping dx,dy small then lexicographic by (dx,dy)
        parity = (int(observation.get("turn_index", 0) or 0) & 1)
        jitter = 0.01 * ((dx == 0 and dy != 0) - (dy == 0 and dx != 0))
        # Scoring: pursuer wants smaller d; evader wants larger d. Clearance helps avoid getting stuck.
        if evader:
            score = d * 10.0 + c * 0.5 + jitter + (0.001 * parity)
        else:
            score = -d * 10.0 + c * 0.5 + jitter - (0.001 * parity)

        key = (-abs(dx) - abs(dy), dx, dy)
        if best_score is None or score > best_score or (score == best_score and key > best):
            best_score = score
            best = key
            best_move = [dx, dy]

    return best_move if best_score is not None else [0, 0]