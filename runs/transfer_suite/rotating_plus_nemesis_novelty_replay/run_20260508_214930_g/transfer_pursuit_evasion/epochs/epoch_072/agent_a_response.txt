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
    far_corner = max(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))

    best_dxdy = (0, 0)
    if is_evader:
        best_score = None
        for dx, dy in deltas:
            if not legal(dx, dy):
                continue
            nx, ny = sx + dx, sy + dy
            s = dist2(nx, ny, ox, oy) + 0.15 * dist2(nx, ny, far_corner[0], far_corner[1])
            # small preference to keep moving rather than stalling when tied
            if dx != 0 or dy != 0:
                s += 0.01
            if best_score is None or s > best_score:
                best_score = s
                best_dxdy = (dx, dy)
    else:
        best_score = None
        for dx, dy in deltas:
            if not legal(dx, dy):
                continue
            nx, ny = sx + dx, sy + dy
            s = -dist2(nx, ny, ox, oy)
            # prefer progress (avoid staying if any equally good chase exists)
            if dx == 0 and dy == 0:
                s -= 0.01
            if best_score is None or s > best_score:
                best_score = s
                best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]