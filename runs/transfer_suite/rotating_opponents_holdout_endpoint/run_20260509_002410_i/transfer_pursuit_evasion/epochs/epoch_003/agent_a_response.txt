def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [w - 1, h - 1])
    x, y = int(self_pos[0]), int(self_pos[1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    obs = set()
    for a, b in observation.get("obstacles", []) or []:
        obs.add((int(a), int(b)))

    my_role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("pursuer" in my_role) or ("pursue" in my_role)

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    def clamp_step(d):
        return 0 if d == 0 else (1 if d > 0 else -1)
    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # Intended move when pursuer: cut off by aiming one step "past" opponent away from us.
    step_away_x = clamp_step(ox - x)
    step_away_y = clamp_step(oy - y)
    tx, ty = ox + step_away_x, oy + step_away_y
    if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in obs:
        tx, ty = ox, oy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_score = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        if is_pursuer:
            score = -d2(nx, ny, tx, ty)  # approach interception target
            # keep pressure: prefer lower direct distance to opponent as secondary
            score -= 0.1 * d2(nx, ny, ox, oy)
            # avoid getting stuck near edges if tied
            score -= 0.01 * (d2(nx, ny, cx, cy))
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]
        else:
            # Evader: maximize distance while gently preferring center to avoid corners/obstacle traps.
            score = d2(nx, ny, ox, oy)
            score -= 0.02 * d2(nx, ny, cx, cy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move