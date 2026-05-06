def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If no resources, drift to reduce opponent advantage toward center-ish.
    cx, cy = (w - 1) // 2, (h - 1) // 2

    best_dxdy = (0, 0)
    best_val = -10**18

    # Precompute resource positions that are valid.
    res = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                res.append((rx, ry))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0

        # Base: prefer moves that move away from being stuck (slight center pull).
        val = - (abs(nx - cx) + abs(ny - cy)) * 0.05

        if res:
            # If we step onto a resource, strongly prioritize.
            for rx, ry in res:
                if nx == rx and ny == ry:
                    val += 1000

            # Steal/contest: maximize (opp_dist - my_dist) for resources where opponent is currently closer,
            # and also keep overall "best my lead" high.
            best_lead = -10**9
            best_steal = -10**9
            closest_my = 10**9
            closest_opp = 10**9
            for rx, ry in res:
                dme = abs(nx - rx) + abs(ny - ry)
                dop = abs(ox - rx) + abs(oy - ry)
                closest_my = dme if dme < closest_my else closest_my
                closest_opp = dop if dop < closest_opp else closest_opp
                lead = dop - dme  # positive means we are closer than opponent
                if lead > best_lead:
                    best_lead = lead
                # "Steal" focus: only resources where opponent was closer from current state.
                # Encourage overtakes even if not maximum overall.
                dme_now = abs(sx - rx) + abs(sy - ry)
                if dop < dme_now and lead > best_steal:
                    best_steal = lead

            # Encourage strong contest and reduce times when opponent is much closer.
            val += best_lead * 2.0
            if best_steal > -10**8:
                val += best_steal * 3.5
            # Mildly prefer reducing our own closest distance while preventing opponent getting closer.
            val += (closest_opp - closest_my) * 0.7
        else:
            val += - (abs(nx - ox) + abs(ny - oy)) * 0.02

        # Deterministic tie-break: prefer staying closer to (0,0) lexicographically on move order.
        key = (-(val), dx, dy)
        if key < (-best_val, best_dxdy[0], best_dxdy[1]):
            best_val = val
            best_dxdy = (dx, dy)

    return [int(best_dxdy[0]), int(best_dxdy[1])]