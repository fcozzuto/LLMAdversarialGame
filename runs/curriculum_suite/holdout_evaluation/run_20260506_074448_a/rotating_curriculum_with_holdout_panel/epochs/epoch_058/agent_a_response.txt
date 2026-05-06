def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def cell_block(x, y):
        return -1000000 if (x, y) in obstacles else 0

    if not resources:
        best = [0, 0]
        best_s = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            # Drift toward the midpoint of remaining space to keep options open
            mx, my = (ox + sx) / 2.0, (oy + sy) / 2.0
            s = -((nx - mx) ** 2 + (ny - my) ** 2)
            if s > best_s or (s == best_s and (dx, dy) < tuple(best)):
                best_s = s
                best = [dx, dy]
        return best

    # Interception-style "race control":
    # For each move, compute best resource lead for us, and worst resource advantage for opponent.
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Score consists of:
        # - primary: maximize our best lead (opp_dist - my_dist) over resources
        # - secondary: if we cannot get a lead, minimize opponent's best lead
        # - tertiary: prefer closer overall to high-lead resources, and avoid stepping into opponent proximity
        my_to_opp = man(nx, ny, ox, oy)

        best_lead = -10**9
        best_cost = 10**9
        opp_best_lead = -10**9
        opp_best_cost = 10**9

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            lead = opd - myd  # positive => we are closer by this margin

            if lead > best_lead or (lead == best_lead and myd < best_cost):
                best_lead = lead
                best_cost = myd

            # Opponent lead from our perspective if they moved similarly; approximate via (my_dist - opp_dist).
            opp_lead = myd - opd  # positive => opponent is closer
            if opp_lead > opp_best_lead or (opp_lead == opp_best_lead and myd < opp_best_cost):
                opp_best_lead = opp_lead
                opp_best_cost = myd

        if best_lead >= 0:
            # We can secure at least one resource first: prioritize lead, then speed.
            val = best_lead * 1000 - best_cost - (3.0 / (1 + my_to_opp))
        else:
            # No lead: reduce opponent's options; prioritize minimizing their best advantage.
            # opp_best_lead is positive when opponent is closer; smaller is better.
            val = -opp_best_lead * 1200 - opp_best_cost - (3.0 / (1 + my_to_opp))

        # Tiny deterministic tie-break: prefer moves that head generally toward our nearest resource.
        # (Avoids jitter between equal values.)
        nrx, nry = min(resources, key=lambda p: man(sx, sy, p[0], p[1]))
        tie = (abs(nx - nrx) + abs(ny - nry))
        val -= tie * 0.001

        if val > best_val or (val == best_val and (dx, dy) < tuple(best_move)):
            best_val = val
            best_move = [dx, dy]

    return best_move