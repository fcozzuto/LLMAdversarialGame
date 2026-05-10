def choose_move(observation):
    w = int(observation.get("grid_width", 1))
    h = int(observation.get("grid_height", 1))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obst_list = observation.get("obstacles") or []
    obstacles = {(int(p[0]), int(p[1])) for p in obst_list if p is not None and len(p) >= 2}
    self_set = observation.get("self_territory") or []
    self_territory = {(int(p[0]), int(p[1])) for p in self_set if p is not None and len(p) >= 2}
    res_list = observation.get("resources") or []
    resources = [(int(p[0]), int(p[1])) for p in res_list if p is not None and len(p) >= 2]
    opp_x, opp_y = int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Precompute closest resource for bias if present
    closest = None
    if resources:
        dmin = 10**18
        for rx, ry in resources:
            dx, dy = rx - sx, ry - sy
            d = dx * dx + dy * dy
            if d < dmin:
                dmin = d
                closest = (rx, ry)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) == (opp_x, opp_y):
            continue

        score = 0
        if (nx, ny) in self_territory:
            score += 3

        # Resource attraction
        if resources and closest is not None:
            rx, ry = closest
            ddx, ddy = rx - nx, ry - ny
            score += 50 - (ddx * ddx + ddy * ddy)  # higher when closer
        else:
            # Center bias
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            ddx, ddy = (nx - cx), (ny - cy)
            score += -int(ddx * ddx + ddy * ddy)

        # Opponent avoidance / contest
        adx, ady = opp_x - nx, opp_y - ny
        ad2 = adx * adx + ady * ady
        if ad2 <= 1:
            score -= 1000
        else:
            score += int(ad2 ** 0.5)  # prefer staying farther

        # Deterministic tie-break: lexicographic on move
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]