def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def best_move_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if dx == 0 and dy == 0:
            return [0, 0]
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        # fall back to axis move if diagonal blocked
        if dx != 0:
            nx2, ny2 = sx + dx, sy
            if 0 <= nx2 < w and (nx2, ny2) not in obstacles:
                return [dx, 0]
        if dy != 0:
            nx2, ny2 = sx, sy + dy
            if 0 <= ny2 < h and (nx2, ny2) not in obstacles:
                return [0, dy]
        return [0, 0]

    if not resources:
        return [0, 0]

    cx, cy = w // 2, h // 2
    best_key = None
    best_t = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)

        # Prefer being strictly closer; punish resources where opponent ties/overtakes
        # Tie-break centers slightly and prefers lower own distance.
        advantage = do - ds  # positive is good

        # Strong penalty if opponent can reach at the same time or sooner
        steal_penalty = 10 if do <= ds else 0

        # Small reward for being near the center (helps sweep-row opponents)
        central_bonus = - (abs(rx - cx) + abs(ry - cy)) * 0.02

        # Deterministic tie-break: larger advantage, then closer ds, then lexicographic position
        key = (-(advantage) - central_bonus + steal_penalty, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    return best_move_toward(tx, ty)