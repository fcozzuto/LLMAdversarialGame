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

    def min_obst_dist(x, y):
        if not obstacles:
            return 999
        dmin = 999
        for ax, ay in obstacles:
            d = abs(ax - x) + abs(ay - y)
            if d < dmin:
                dmin = d
                if dmin == 0:
                    return 0
        return dmin

    # Targets: pursuer wants to get opponent "cornered" (near its own target corner),
    # evader wants the farthest corner from the pursuer.
    if is_evader:
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        # Choose corner that is closest to opponent (to reduce its mobility) and prefer approaching it.
        tx, ty = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_opp = abs(ox - nx) + abs(oy - ny)
        d_corner = abs(tx - nx) + abs(ty - ny)
        md = min_obst_dist(nx, ny)

        # Heuristic scoring:
        # - pursuer: minimize opponent distance; also reduce distance to chosen corner; avoid obstacles
        # - evader: maximize opponent distance; also increase distance from chosen corner (escape) and obstacles
        if is_evader:
            val = (d_opp * 1000) + (d_corner * 5) + (md * 2) + (dx * (tx - nx) * -0 + dy * (ty - ny) * -0)
        else:
            val = (-d_opp * 1000) + (-d_corner * 5) + (md * 2)

        # Additional tie-breaker to reduce oscillation: prefer moves that change position in the
        # direction of the primary goal axis (x or y) based on relative positions.
        if not is_evader:
            # primary axis toward opponent
            if abs(ox - sx) >= abs(oy - sy):
                val += -0.01 * (1 if (dx != 0 and (ox - sx) * dx > 0) else 0)
            else:
                val += -0.01 * (1 if (dy != 0 and (oy - sy) * dy > 0) else 0)
        else:
            # move away from opponent along dominant axis
            if abs(ox - sx) >= abs(oy - sy):
                val += 0.01 * (1 if (dx != 0 and (ox - sx) * dx < 0) else 0)
            else:
                val += 0.01 * (1 if (dy != 0 and (oy - sy) * dy < 0) else 0)

        if best is None or (val > best_val):
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]