def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in role) or ("pursur" in role)

    obst = set()
    for p in observation.get("obstacles", []):
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best_move = (0, 0)
    best_val = None

    # Opponent policy assumption: evader maximizes distance from us; pursuer minimizes.
    opp_wants_min = not pursuer

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if nx == ox and ny == oy:
            return [dx, dy]  # immediate capture (capture_radius=0)

        # Evaluate our move under worst-case opponent response.
        worst = None
        for odx, ody in deltas:
            ex, ey = ox + odx, oy + ody
            if not legal(ex, ey):
                continue
            d = dist2(nx, ny, ex, ey)
            # If opponent pursues, they minimize distance; else maximize.
            val = d if not opp_wants_min else -d
            if worst is None:
                worst = val
            else:
                worst = val if (opp_wants_min and val < worst) or ((not opp_wants_min) and val > worst) else worst

        # Our objective: if we are pursuer, minimize distance; if evader, maximize.
        our_val = -worst if pursuer else worst
        if best_val is None or our_val > best_val or (our_val == best_val and (dx, dy) < best_move):
            best_val = our_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]