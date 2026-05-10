def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    role = observation.get("self_role", "pursuer")
    is_evader = (role == "evader")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obst_score(x, y):
        if not obstacles:
            return 3
        dmin = 999
        for ax, ay in obstacles:
            d = abs(ax - x) + abs(ay - y)
            if d < dmin:
                dmin = d
                if dmin <= 1:
                    break
        return dmin

    # Deterministic corner target to shape behavior
    if is_evader:
        cx, cy = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        cx, cy = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        dist_opp = abs(nx - ox) + abs(ny - oy)
        if not is_evader:
            if dist_opp == 0:
                val = 10**6
            else:
                val = -dist_opp
                val += 0.15 * (- (abs(cx - nx) + abs(cy - ny)) )  # move toward chosen corner
                val += 0.02 * obst_score(nx, ny)
        else:
            if dist_opp == 0:
                val = -10**6
            else:
                val = dist_opp
                val += 0.12 * ((abs(cx - nx) + abs(cy - ny)) )  # stay far from corner-chasing
                val += 0.03 * obst_score(nx, ny)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move