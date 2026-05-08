def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    srole = (observation.get("self_role") or "").lower()
    evader = ("evader" in srole) or ("evasion" in srole) or ("runner" in srole)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    safe_corners = [c for c in corners if c not in obst]
    if not safe_corners:
        safe_corners = corners[:]

    target_corner = None
    best_corner_d2 = None
    for cx, cy in safe_corners:
        ddx, ddy = sx - cx, sy - cy
        d2 = ddx * ddx + ddy * ddy
        # Prefer moving toward a corner that is far from pursuer/opponent when evading
        # When pursuing, still just set a target corner farthest from evader to "trap" it.
        opp_dx, opp_dy = ox - cx, oy - cy
        opp_d2 = opp_dx * opp_dx + opp_dy * opp_dy
        # For evader: maximize opponent distance from our target corner.
        # For pursuer: minimize opponent distance to our target corner (so it's more "cornerable").
        score = opp_d2 if evader else -opp_d2
        if best_corner_d2 is None or score > best_corner_d2:
            best_corner_d2 = score
            target_corner = (cx, cy)
    tx, ty = target_corner

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue

        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy
        md = abs(nx - ox) + abs(ny - oy)
        toward_corner = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)

        if evader:
            # Increase distance from opponent; also reduce distance to our chosen corner (cornering).
            score = d2 * 3 - md - toward_corner * 0.7
        else:
            # Reduce distance to opponent; also move so opponent is more likely to be driven toward our target corner.
            # Equivalent: prioritize our move that decreases our distance and also reduces distance from our move to target corner.
            score = (-d2) * 3 - md * 1.2 - toward_corner * 0.2

        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]