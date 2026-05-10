def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            resources.append((int(r[0]), int(r[1])))
        except Exception:
            pass

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None

    if not resources:
        # Deterministic fallback: drift toward whichever corner is farther from opponent (to avoid being blocked).
        tx, ty = (0, 0) if ((ox + oy) & 1) == 0 else (w - 1, h - 1)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Choose move by local 1-step lookahead: maximize lead on best reachable resource, while avoiding immediate obstacle hits.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # If we can land on a resource this turn, prioritize it strongly.
        hit_res = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                hit_res = 1
                break

        # After moving, compute best lead score among resources.
        our_best = 10**9
        opp_best = 10**9
        best_lead = -10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds
            if ds < our_best:
                our_best = ds
            if do < opp_best:
                opp_best = do
            # Prefer positive lead (we can arrive no later), then closer arrival, then smaller opponent distance.
            # Also prefer resources that are relatively "urgent" where opponent is not too far.
            cand = (lead, -ds, -do, -(abs(rx - ox) + abs(ry - oy)))
            if lead > best_lead:
                best_lead = lead
                best_pair = cand
            else:
                # deterministically compare when leads equal-ish
                if lead == best_lead:
                    if cand > best_pair:
                        best_pair = cand

        # Key: immediate collection > improve lead > minimize our distance; slight tie-break toward moving generally toward center-ish.
        center_bias = - (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))
        key = (hit_res, best_pair[0], best_pair[1], best_pair[2], center_bias, -our_best)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]