def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    # If role strings are unclear, infer: if we likely are pursuer when our score gain on capture exists,
    # but we don't have that; default to evasion behavior (safer against direct pursuit).
    is_evader = ("evader" in self_role) or ("pursuer" not in self_role and "pursuer" in opp_role) or (self_role == "")
    is_pursuer = not is_evader

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    near_corner = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    tx, ty = far_corner if is_evader else near_corner

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        # Target preference: evader wants far corner; pursuer wants near corner (towards opponent).
        d_t = dist2(nx, ny, tx, ty)

        # Tie-break deterministically: prefer staying still last (so movement chosen when equal).
        stay_pen = 0 if (dx != 0 or dy != 0) else -1

        if is_evader:
            val = 5.0 * d_opp - 0.08 * d_t + stay_pen
            # If moving increases both distance and towards far corner, boost.
            if d_opp > dist2(sx, sy, ox, oy):
                val += 1.0
        else:
            val = -5.0 * d_opp - 0.08 * d_t + stay_pen
            if d_opp < dist2(sx, sy, ox, oy):
                val += 1.0

        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        # Fallback: stay put
        return [0, 0]
    return best