def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    if w < 1 or h < 1 or len(sp) < 2 or len(op) < 2:
        return [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evader = ("evader" in role) or ("runner" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None

    def obstacle_clearance(x, y):
        md = 10**9
        for (ax, ay) in obstacles:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md if md != 10**9 else 99

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        clr = obstacle_clearance(nx, ny)
        # Main objective: maximize/minimize distance to opponent.
        # Secondary: move to safer tiles when evading, or avoid tight spots when pursuing.
        score = (dist if evader else -dist) + (0.05 * clr if evader else -0.05 * clr)
        key = (-score, dx, dy) if evader else (-score, dx, dy)
        # Deterministic tie-break: smallest (dx,dy) among equal scores via key.
        if best is None or key < best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])] if best is not None else [0, 0]