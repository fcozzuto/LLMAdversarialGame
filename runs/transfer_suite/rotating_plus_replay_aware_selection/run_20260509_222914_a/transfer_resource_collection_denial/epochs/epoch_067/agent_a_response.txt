def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs_cells = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs_cells.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs_cells:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_cells

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target(myx, myy, oppx, oppy):
        best = None
        for rx, ry in resources:
            sd = cheb_dist(myx, myy, rx, ry)
            od = cheb_dist(oppx, oppy, rx, ry)
            # Prefer resources where we beat opponent's arrival; then maximize margin; then minimize our distance.
            margin = od - sd
            val = (margin, -sd, -cheb_dist(oppx, oppy, rx, ry))
            if best is None or val > best[0]:
                best = (val, (rx, ry), sd, od)
        return best

    # Evaluate each possible move by its effect on the best attainable resource.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        target = best_target(nx, ny, ox, oy)
        (margin, neg_sd, neg_od2), (rx, ry), sd, od = target

        # Secondary: avoid stepping into opponent's near-term contest zone.
        opp_next_best = best_target(nx, ny, ox, oy)
        opp_risk = cheb_dist(ox, oy, rx, ry)

        # Score: primarily win margin, then close our distance, and also slightly reduce risk.
        score = (margin, -sd, -opp_risk, -abs(nx - rx) - abs(ny - ry))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]