def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in self_role) or (self_role == "evader") or ("purs" in opponent_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def is_blocked(x, y):
        return (x, y) in obstacles

    # For evader, bias toward farthest corner; for pursuer, bias toward opponent.
    target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy)) if self_is_evader else None

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if is_blocked(nx, ny):
            continue

        d_op = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, target_corner[0], target_corner[1]) if self_is_evader else 0

        # Also consider distance from obstacles (softly), to avoid sliding into tight areas.
        near_obs = 0
        if obstacles:
            for (px, py) in obstacles:
                t = dist2(nx, ny, px, py)
                if t == 0:
                    near_obs = -999999
                    break
                near_obs = min(near_obs, t) if near_obs else t
            if near_obs == 0:
                near_obs = 0
        else:
            near_obs = 0

        if self_is_evader:
            # Maximize distance to opponent; tie-break by minimizing distance to target corner.
            score = d_op * 1000 - d_corner - near_obs // 4
        else:
            # Minimize distance to opponent; tie-break by making progress also in direction to opponent.
            score = -d_op * 1000 + (w * w + h * h - d_corner) - near_obs // 4

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move