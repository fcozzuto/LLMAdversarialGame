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

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    if self_is_evader:
        target_x, target_y = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        best_val = -10**18
    else:
        target_x, target_y = ox, oy
        best_val = 10**18

    best_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue
        if self_is_evader:
            # maximize separation; also prefer corner escape to avoid zigzag trapping
            sep = dist2(nx, ny, ox, oy)
            corner_push = -dist2(nx, ny, target_x, target_y)
            # small bias: keep moving generally away from pursuer
            away = (nx - ox) * (sx - ox) + (ny - oy) * (sy - oy)
            val = sep * 10 + corner_push * 2 + (away)
            if val > best_val:
                best_val = val
                best_moves = [[dx, dy]]
            elif val == best_val:
                best_moves.append([dx, dy])
        else:
            # minimize separation; break ties by steering toward opponent and staying out of obstacles
            sep = dist2(nx, ny, ox, oy)
            toward = -(dist2(nx, ny, target_x, target_y))
            # prefer not to "overshoot" by slightly penalizing increasing manhattan too much
            man = abs(nx - ox) + abs(ny - oy)
            prev_man = abs(sx - ox) + abs(sy - oy)
            overshoot_pen = man - prev_man
            val = sep * 10 + overshoot_pen - toward
            if val < best_val:
                best_val = val
                best_moves = [[dx, dy]]
            elif val == best_val:
                best_moves.append([dx, dy])

    if best_moves:
        return best_moves[0]
    return [0, 0]