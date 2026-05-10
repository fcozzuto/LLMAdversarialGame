def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    self_role = observation.get("self_role") or ""
    role = self_role.lower()

    obstacles = observation.get("obstacles") or []
    ob = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in ob:
            candidates.append((nx, ny, dx, dy))
    if not candidates:
        return [0, 0]

    def manhattan(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # If we are evader: maximize distance; prefer toward center to avoid cornering too early.
    # If we are pursuer: minimize distance; avoid moves that step into immediate dead-ends when possible.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    center_dist = lambda x, y: abs(x - cx) + abs(y - cy)

    best = None
    best_val = None
    for nx, ny, dx, dy in candidates:
        d = manhattan(nx, ny, ox, oy)
        if "evader" in role:
            primary = d
            # tie-breakers: move away even if distance equal; then closer to center; then lexicographic
            val = (primary, center_dist(nx, ny), dx, dy)
            # We want maximize primary and minimize center_dist, so invert appropriately:
            key = (primary, -val[1], -dx, -dy)
        else:
            primary = -d
            # tie-break: prefer moves that reduce distance and move toward center a bit to keep mobility
            key = (primary, -center_dist(nx, ny), -dx, -dy)
        if best is None:
            best, best_val = (dx, dy), key
        else:
            if key > best_val:
                best, best_val = (dx, dy), key

    return [int(best[0]), int(best[1])]