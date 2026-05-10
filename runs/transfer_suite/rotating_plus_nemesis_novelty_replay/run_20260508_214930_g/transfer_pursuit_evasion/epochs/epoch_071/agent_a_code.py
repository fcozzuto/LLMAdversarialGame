def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    self_role = (observation.get("self_role", "") or "").lower()
    is_evader = "evader" in self_role
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

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = min(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))

    best = None
    best_score = None
    for dx, dy in deltas:
        if not legal(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        if is_evader:
            # maximize distance from pursuer; also prefer escaping toward farthest corner deterministically
            score = dist2(nx, ny, ox, oy)
            score = score * 1000 + dist2(nx, ny, target_corner[0], target_corner[1])
            key = score
            better = best is None or key > best_score
        else:
            # pursue while pressuring the evader's nearest corner to reduce escape options
            after = dist2(nx, ny, ox, oy)
            corner_pressure = dist2(nx, ny, target_corner[0], target_corner[1])
            # prioritize distance first, then corner pressure
            key = -(after * 1000 + corner_pressure)
            better = best is None or key > best_score
        if better:
            best_score = key
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best