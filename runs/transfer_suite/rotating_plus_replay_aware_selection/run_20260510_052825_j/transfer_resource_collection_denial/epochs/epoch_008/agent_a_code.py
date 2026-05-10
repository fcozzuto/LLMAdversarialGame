def choose_move(observation):
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles_list = observation.get('obstacles', []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        v = a - c
        if v < 0:
            v = -v
        u = b - d
        if u < 0:
            u = -u
        return v + u

    if not resources:
        return [0, 0]

    def clamp(v, lo, hi):
        if v < lo:
            return lo
        if v > hi:
            return hi
        return v

    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            # engine will reject/keep, but we still treat it as worst to avoid it
            continue

        self_nearest = 10**9
        opp_nearest = 10**9
        best_val = -10**18
        for r in resources:
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Favor grabbing resources you can reach first; heavily discourage targets opponent is much closer to.
            rel = od - sd
            # Small bonus for closer to finish; small tie-break toward resources that are further from opponent.
            val = (rel * 100) - (sd * 2) + (od * 0.2)
            # If opponent is already significantly closer, make it a low priority.
            if od + 0 < sd:
                val -= 250
            if rel > 0:
                self_nearest = min(self_nearest, sd)
            opp_nearest = min(opp_nearest, od)
            if val > best_val:
                best_val = val

        # If none had positive relative gain, still move toward the closest "least-losing" option deterministically.
        if best_val < -10**17:
            # choose closest by minimizing (sd - od) and then sd
            worst = (10**18, 10**18)
            for r in resources:
                rx, ry = r[0], r[1]
                if (rx, ry) in obstacles:
                    continue
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                worst = min(worst, (sd - od, sd))
            best_val = -worst[0] * 100 - worst[1]

        # Anti-stall nudge: prefer moves that reduce distance to the best resource by your current target logic.
        best = max(best, (best_val, dx, dy))

    _, dx, dy = best
    return [int(dx), int(dy)]