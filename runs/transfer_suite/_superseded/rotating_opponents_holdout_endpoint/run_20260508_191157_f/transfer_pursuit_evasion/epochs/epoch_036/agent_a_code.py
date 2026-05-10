def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    role = observation.get("self_role", "pursuer")

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Deterministic tie-break: prefer moves that keep/approach main direction, then lexicographic.
    deltas.sort(key=lambda t: (abs(t[0]) + abs(t[1]) == 0, t[0], t[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def mobility(x, y):
        cnt = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                cnt += 1
        return cnt

    def obs_prox(x, y):
        if not obs_set:
            return 99
        md = 10**9
        for ax, ay in obs_set:
            d = abs(ax - x) + abs(ay - y)
            if d < md:
                md = d
                if md <= 1:
                    break
        return md

    def score_for_move(nx, ny):
        d = man(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        prox = obs_prox(nx, ny)
        # For pursuer: minimize distance; for evader: maximize distance.
        # Also prefer higher mobility and stay away from obstacles (prox small => risky).
        if role == "pursuer":
            return (-d * 10.0) + (mob * 1.5) + (prox * -0.6)
        else:
            return (d * 10.0) + (mob * 1.5) + (prox * -0.6)

    best_move = [0, 0]
    best_val = None

    # One-step lookahead against a "greedy" opponent response: deterministic approximation.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        base = score_for_move(nx, ny)

        # Approximate opponent: if we are pursuer, opponent likely evades; if we are evader, opponent likely pursues.
        # Apply a small penalty if opponent can move to reduce our next objective quickly.
        opp_best = None
        for odx, ody in deltas:
            ex, ey = ox + odx, oy + ody
            if not inb(ex, ey) or (ex, ey) in obs_set:
                continue
            if role == "pursuer":
                # opponent evades: maximize distance to our new position
                val = man(ex, ey, nx, ny)
            else:
                # opponent pursues: minimize distance to our new position
                val = -man(ex, ey, nx, ny)
            if opp_best is None or val > opp_best[0]:
                opp_best = (val, odx, ody)
        if opp_best is None:
            look_pen = 0.0
        else:
            if role == "pursuer":
                # opponent evades => reduce our score by (distance our move causes opponent to keep)
                look_pen = (1.0 / (1 + man(ox + opp_best[1], oy + opp_best[2], nx, ny))) * 6.0
            else:
                look_pen = 0.0

        val = base - look_pen

        if best_val is None or val > best_val + 1e-12:
            best_val = val
            best_move = [dx, dy]

    return best_move