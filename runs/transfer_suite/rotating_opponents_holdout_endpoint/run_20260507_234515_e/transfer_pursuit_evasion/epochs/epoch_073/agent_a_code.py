def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                oset.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in oset

    self_role = str(observation.get("self_role", "") or "")
    is_evader = ("evader" in self_role.lower()) or ("evasion" in str(observation.get("environment_name", "")).lower())
    cap_r = int(observation.get("capture_radius", 0) or 0)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def nearest_corner_dist(nx, ny):
        return min(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)

    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            if cap_r == 0 and nx == ox and ny == oy:
                continue
            dist = abs(nx - ox) + abs(ny - oy)
            # Tie-breakers: corner control + avoid moving into open space near opponent
            corner_d = nearest_corner_dist(nx, ny)
            # pursuer: minimize dist; evader: maximize dist
            primary = dist if not is_evader else -dist
            # Prefer being closer to corner for pursuer (to corner the evader), but farther for evader
            secondary = corner_d if not is_evader else -corner_d
            # Deterministic slight preference to not stay still unless forced
            staying_pen = 1 if (dx == 0 and dy == 0) else 0
            score = (primary, secondary, staying_pen)
            if best is None or score < best[0]:
                best = (score, (dx, dy))

    if best is None:
        return [0, 0]
    return [int(best[1][0]), int(best[1][1])]