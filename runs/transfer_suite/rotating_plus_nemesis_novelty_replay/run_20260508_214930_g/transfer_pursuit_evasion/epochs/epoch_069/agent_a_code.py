def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    self_role = observation.get("self_role", "")
    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(dx, dy):
        nx, ny = sx + dx, sy + dy
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    pursuer = ("pursuer" in (self_role or "").lower()) or ("pursuit" in (self_role or "").lower())
    # If roles are unknown, default to pursuit behavior (safe and competitive).
    if not (pursuer or ("evader" in (self_role or "").lower())):
        pursuer = True

    best = None
    best_key = None
    for dx, dy in deltas:
        if not legal(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        d = dist2(nx, ny, ox, oy)
        # pursuer: minimize distance; evader: maximize distance
        score = d if not pursuer else -d
        # slight bias: avoid moving into opponent "line" by preferring larger x+y difference for evader,
        # and smaller for pursuer; deterministic tie-break using dx,dy order index.
        line = (nx + ny) - (ox + oy)
        line_term = (abs(line) if not pursuer else -abs(line))
        key = (score, line_term, -abs(dx), -abs(dy), dx, dy) if pursuer else (score, line_term, abs(dx), abs(dy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]