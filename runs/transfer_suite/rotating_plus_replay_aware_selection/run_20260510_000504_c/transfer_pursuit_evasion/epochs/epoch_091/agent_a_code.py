def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in self_role) or ("escape" in self_role) or ("runner" in self_role) or ("flee" in self_role)

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    corner = max(corners, key=lambda c: dist2(c[0], c[1])) if is_evader else min(corners, key=lambda c: dist2(c[0], c[1]))
    tx, ty = corner

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        d_now = dist2(sx, sy)
        d_next = dist2(nx, ny)
        corner_bias = (abs(tx - sx) + abs(ty - sy)) - (abs(tx - nx) + abs(ty - ny))

        if is_evader:
            score = (d_next - d_now) * 1000 + corner_bias * 2
        else:
            score = (d_now - d_next) * 1000 + corner_bias * (-2)

        if best_score is None or score > best_score or (score == best_score and (dx != 0 or dy != 0)):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]