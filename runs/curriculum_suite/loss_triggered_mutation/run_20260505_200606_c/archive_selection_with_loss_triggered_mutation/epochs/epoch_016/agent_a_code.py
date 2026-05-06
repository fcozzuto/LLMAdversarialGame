def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    # obstacle "roughness": avoid stepping near obstacles to reduce path loss vs greedy opponent
    def obstacle_risk(x, y):
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    r += 1
        return r

    if not resources:
        return [0, 0]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or not ok(nx, ny):
            continue

        my_r = obstacle_risk(nx, ny)

        # Choose a target with maximal "lead" (how much closer we are than opponent)
        lead_best = -10**9
        opp_far_best = -10**9
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)

            # Prefer resources we can reach sooner (or at least not slower), then maximize lead.
            lead = opd - myd

            # If lead is not good, aim for resources that keep opponent far from them.
            opp_far = opd - 0.5 * myd

            if lead > lead_best:
                lead_best = lead
            if opp_far > opp_far_best:
                opp_far_best = opp_far

        # Deterministic tie-breakers: prefer moving toward center slightly, and reduce obstacle risk.
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))

        # Key encourages material strategic shift vs greedy pursuit: maximize lead first; if none, maximize opp_far.
        # Add slight center term and penalize risk.
        if lead_best >= 1:
            key = (-0, -lead_best, my_r, -center, dx, dy)
            score_group = 0
        else:
            key = (1, -opp_far_best, my_r, -center, dx, dy)
            score_group = 1

        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best else [0, 0]