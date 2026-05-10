def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    blocked = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            blocked.add((int(o[0]), int(o[1])))

    self_role = (observation.get("self_role", "") or "").lower()
    opponent_role = (observation.get("opponent_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("purs" in opponent_role and "evad" in self_role) or ("evad" in opponent_role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    best = None
    best_move = [0, 0]
    # Deterministic tie-break: fixed order in deltas, maximize/minimize score accordingly
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        d = dist2((nx, ny), (ox, oy))
        if is_evader:
            # Prefer farther from pursuer; slight preference for moving to center to avoid corner pinning
            center_bonus = (3.5 - abs(nx - 3.5)) + (3.5 - abs(ny - 3.5))
            score = d * 10.0 + center_bonus * 0.01
        else:
            # Prefer closer to pursuer; also prefer aligning diagonally (more direct capture)
            score = -d * 10.0
            if dx != 0 and dy != 0:
                score += 0.01
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move if best is not None else [0, 0]