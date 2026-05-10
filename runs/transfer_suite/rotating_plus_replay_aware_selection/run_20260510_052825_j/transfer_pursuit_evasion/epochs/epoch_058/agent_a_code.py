def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opp_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in self_role) or (self_role == "evader") or ("purs" in opp_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_penalty(x, y):
        pen = 0
        for ax in (x - 1, x, x + 1):
            for ay in (y - 1, y, y + 1):
                if (ax, ay) in obstacles:
                    pen += 3
        return pen

    best_score = None
    best_move = [0, 0]
    # Tie-break deterministically: prefer larger dx then larger dy then smaller dist.
    for dx, dy in deltas:
        tx, ty = sx + dx, sy + dy
        if not (0 <= tx < w and 0 <= ty < h):
            continue
        if (tx, ty) in obstacles:
            continue

        d = dist2(tx, ty, ox, oy)
        score = d if self_is_evader else -d

        # Prefer moves that keep away from nearby obstacles (both roles benefit).
        score -= obstacle_penalty(tx, ty) * (1 if self_is_evader else 1)

        # Encourage moving toward/away from the board center to reduce wall-trapping.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dc = dist2(tx, ty, cx, cy)
        if self_is_evader:
            score -= 0.02 * dc  # stay spread out rather than hugging center; wall runner likes corners
        else:
            score -= 0.01 * dc

        cand = (score, dx, dy, -d)
        if best_score is None or cand > best_score:
            best_score = cand
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]