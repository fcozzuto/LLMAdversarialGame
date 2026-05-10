def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles}

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    def is_pursuer(role):
        r = role.replace("-", "_")
        return ("purs" in r) or (r == "pursuer")
    def is_evader(role):
        r = role.replace("-", "_")
        return ("evad" in r) or (r == "evader")

    pursuer = is_pursuer(self_role) and not is_evader(self_role)
    if not pursuer and is_pursuer(opp_role) and not is_evader(opp_role):
        pursuer = False
    elif not pursuer and is_pursuer(opp_role) and is_evader(opp_role):
        pursuer = True
    elif pursuer and is_evader(self_role):
        pursuer = False

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    tx = ox + (ox - sx)
    ty = oy + (oy - sy)
    tx = clamp(tx, 0, w - 1)
    ty = clamp(ty, 0, h - 1)

    # If we're the evader, flip the anticipation direction.
    if not pursuer:
        tx = ox - (ox - sx)
        ty = oy - (oy - sy)
        tx = clamp(tx, 0, w - 1)
        ty = clamp(ty, 0, h - 1)

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    best = None
    best_val = None

    for dx in dxs:
        for dy in dys:
            nx = sx + dx
            ny = sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obs:
                continue

            # Main goal: move relative to anticipated target.
            val = dist2(nx, ny, tx, ty)

            # Secondary: avoid letting pursuer get closer too easily (or for pursuer: get closer faster).
            if pursuer:
                val += 0.35 * dist2(nx, ny, ox, oy)
            else:
                val -= 0.35 * dist2(nx, ny, ox, oy)

            # Tiny tie-breaker to prefer diagonal toward target direction.
            val += 0.001 * (0 if dx != 0 and dy != 0 else 1)

            if best_val is None or val < best_val:
                best_val = val
                best = [dx, dy]

    if best is None:
        return [0, 0]
    return best