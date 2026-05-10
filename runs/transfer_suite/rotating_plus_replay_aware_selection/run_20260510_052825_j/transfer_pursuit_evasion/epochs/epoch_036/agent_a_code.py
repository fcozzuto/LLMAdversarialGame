def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opponent_role = str(observation.get("opponent_role") or "").lower()
    if ("evad" in self_role) or self_role == "evader":
        mode = "evade"
    elif ("purs" in self_role) or self_role == "pursuer":
        mode = "pursue"
    else:
        mode = "pursue" if ("purs" in opponent_role) or opponent_role == "pursuer" else "evade"

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(x1, y1, x2, y2):
        dx, dy = abs(x1 - x2), abs(y1 - y2)
        return dx if dx > dy else dy

    def blocked(x, y):
        return (x, y) in obs

    # Prefer legal non-blocked moves; if none, allow staying (engine keeps position if illegal)
    best = None
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        legal = not blocked(nx, ny)
        d = dist_cheb(nx, ny, ox, oy)

        # tie-breaker: also keep away from obstacles when possible
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obs:
                    near_obs += 1

        if mode == "pursue":
            # smaller distance better; legal moves slightly preferred
            score = (0 if legal else -1, -(d * 10 + near_obs))
        else:
            # larger distance better; legal moves slightly preferred
            score = (0 if legal else -1, (d * 10 - near_obs))

        if best is None or score[0] > best_score[0] or (score[0] == best_score[0] and score[1] > best_score[1]):
            best = [dx, dy]
            best_score = score

    if best is not None:
        return best
    return [0, 0]