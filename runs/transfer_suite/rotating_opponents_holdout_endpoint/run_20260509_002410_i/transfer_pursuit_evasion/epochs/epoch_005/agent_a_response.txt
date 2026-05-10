def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    x, y = int(sx), int(sy)
    ex, ey = int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for a in obstacles:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            obs.add((int(a[0]), int(a[1])))

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("pursue" in role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best = None
    best_score = None
    # Deterministic tie-break: lexicographic over (dx,dy) via deltas order.
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        dist = d2(nx, ny, ex, ey)
        # Pursuer wants smaller distance; evader wants larger distance.
        # Slight preference for advancing the line toward opponent corner.
        corner_bias = (nx + ny) if (ex + ey) > (w - 1 + h - 1) / 2 else (-(nx + ny))
        score = -dist if pursuer else dist
        score += 0.001 * corner_bias
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    # If all moves blocked (unlikely), stay.
    return best if best is not None else [0, 0]