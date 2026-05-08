def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))

    sx, sy = self_pos
    ox, oy = opp_pos

    sr = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in sr) or ("hunter" in sr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target_corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def clamp_in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def valid(nx, ny):
        return clamp_in_bounds(nx, ny) and (nx, ny) not in obstacles

    best = None
    if pursuer:
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            score = -d
            if best is None or score > best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
    else:
        # Evader: run to the corner farthest from pursuer, while maximizing distance.
        tcx, tcy = max(target_corners, key=lambda c: dist2(c[0], c[1], ox, oy))
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_opp = dist2(nx, ny, ox, oy)
            d_corner = dist2(nx, ny, tcx, tcy)
            score = d_opp * 1000 - d_corner
            if best is None or score > best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)

    if best is None:
        # If all moves blocked, stay.
        return [0, 0]
    return [int(best[0]), int(best[1])]