def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Prefer resources where we arrive earlier than opponent; if none, go for closest.
    best = None
    best_key = None
    for t in res:
        sd = dist((sx, sy), t)
        od = dist((ox, oy), t)
        # Add a small tie-break to prefer higher "swing" control near midgame.
        key = (od - sd, -sd, t[0], t[1])
        if best_key is None or key > best_key:
            best_key = key
            best = t
    tx, ty = best

    # Greedy next step: avoid obstacles; minimize distance to target (Chebyshev movement).
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                d = max(abs(tx - nx), abs(ty - ny))
                moves.append((d, abs(tx - nx) + abs(ty - ny), dx, dy))
    if not moves:
        return [0, 0]
    moves.sort()
    _, _, dx, dy = moves[0]

    # If we are not meaningfully ahead on this target and staying might help maneuver, allow occasional hold.
    turns = int(observation.get("turn_index", 0))
    sd0 = dist((sx, sy), best)
    od0 = dist((ox, oy), best)
    if od0 - sd0 <= 0 and (turns % 2 == 0):
        return [0, 0]
    return [dx, dy]