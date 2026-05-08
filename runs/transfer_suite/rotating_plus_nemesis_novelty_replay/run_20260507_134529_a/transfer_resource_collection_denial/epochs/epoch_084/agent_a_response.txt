def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    blocked = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    resources = observation.get("resources") or []

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        # Intercept: move to reduce distance to opponent, but also avoid dead ends near obstacles.
        best = None
        best_move = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            val = dist(nx, ny, ox, oy)
            if best is None or val < best:
                best = val
                best_move = [dx, dy]
        return best_move

    # Evaluate each candidate by best "resource race" advantage.
    # If we're behind on a resource, prefer moves that reduce the opponent's lead (deny by interception).
    best_val = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        best_res = None
        for r in resources:
            rx, ry = r[0], r[1]
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Advantage: positive means we are closer right now.
            adv = od - sd
            # Prefer winning (large adv), but if no winning resource, minimize opponent advantage.
            # Also prefer getting closer to resources generally.
            val = adv * 10 - sd
            # Deny pressure: when behind (adv negative), reduce opp's effective advantage.
            val += -max(0, -adv) * 0.5 + 0.02 * (od)  # small bias toward resources opponent would like
            if best_res is None or val > best_res:
                best_res = val

        # Secondary tie-break: be closer to the nearest resource (faster collection).
        near_sd = min(dist(nx, ny, r[0], r[1]) for r in resources)
        cand = (best_res, -near_sd, -dist(nx, ny, ox, oy))
        if best_val is None or cand > best_val:
            best_val = cand
            best_move = [dx, dy]

    return best_move