def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = []
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.append((x, y))
    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("runner" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    parity = int(observation.get("turn_index", 0) or 0) & 1

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obstacle_penalty(x, y):
        if not obstacles:
            return 0.0
        # strong repulsion if too close to obstacles; prefer keeping away
        best = 10**9
        for ax, ay in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < best:
                best = d
        if best <= 1:
            return 50.0
        if best == 2:
            return 10.0
        if best == 3:
            return 4.0
        return 0.0

    # Deterministic tie-break: slight directional preference by parity
    pref = [(1, 0), (0, 1), (-1, 0), (0, -1)] if parity == 0 else [(0, 1), (1, 0), (0, -1), (-1, 0)]
    pref_map = {d: i for i, d in enumerate(pref)}

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            nx, ny = sx, sy  # engine keeps in place if invalid
        d = manhattan(nx, ny, ox, oy)
        obs_pen = obstacle_penalty(nx, ny)
        # score: evader maximizes distance; pursuer minimizes distance
        # also avoid obstacles; tiny preference to break ties deterministically
        tie = pref_map.get((dx, dy), 10)
        val = (d if evader else -d) - obs_pen - 0.01 * tie
        if best_val is None or (val > best_val if evader else val > best_val):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]