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
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def nearest_corner_score(x, y):
        # If evader: prefer corners far from opponent; else prefer corners close to opponent.
        best = None
        for cx, cy in corners:
            dco = dist2(cx, cy, ox, oy)
            # score higher is better
            s = dco if self_is_evader else -dco
            # tie-break: also consider being closer to that corner
            s += (-(dist2(x, y, cx, cy)) if self_is_evader else -(dist2(x, y, cx, cy)) * 0.5)
            if best is None or s > best:
                best = s
        return best if best is not None else 0.0

    def obstacle_proximity_penalty(x, y):
        # Small penalty for being adjacent to obstacles (evader) or for moving too close to them (pursuer).
        # Keeps behavior stable with minimal computation.
        pen = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                pen += 1
        return pen

    best = None  # (score, dx, dy)
    # primary: distance; secondary: corner bias; tertiary: obstacle proximity; final: deterministic tie-break
    for dx, dy in deltas:
        tx, ty = sx + dx, sy + dy
        if not (0 <= tx < w and 0 <= ty < h):
            continue
        if (tx, ty) in obstacles:
            continue

        d = dist2(tx, ty, ox, oy)
        primary = d if self_is_evader else -d
        corner_b = nearest_corner_score(tx, ty) * (1.0 if self_is_evader else 0.7)
        obs_pen = obstacle_proximity_penalty(tx, ty)
        # evader: avoid obstacles more; pursuer: avoid obstacles slightly to reduce getting trapped
        tertiary = (-obs_pen if self_is_evader else -0.5 * obs_pen)

        # mild preference for moving if it doesn't reduce primary too much
        move_pref = 0.02 if (dx != 0 or dy != 0) else 0.0

        score = primary + corner_b + tertiary + move_pref

        if best is None or score > best[0] or (score == best[0] and (dx, dy) > (best[1], best[2])):
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]