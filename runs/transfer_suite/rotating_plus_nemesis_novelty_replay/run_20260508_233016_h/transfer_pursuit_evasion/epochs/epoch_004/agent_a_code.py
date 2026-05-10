def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("evad" not in self_role and "evad" in opp_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if (int(observation.get("turn_index", 0)) & 1) == 1:
        deltas = list(reversed(deltas))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def min_obs_dist(x, y):
        if not obs:
            return 9
        md = 999
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d < md:
                md = d
        return md

    def free_neighbors(x, y):
        cnt = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                cnt += 1
        return cnt

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        mo = min_obs_dist(nx, ny)
        fn = free_neighbors(nx, ny)

        if pursuer:
            # chase while staying mobile and away from obstacles
            score = (-d_to_opp * 10) + (mo * 1.5) + (fn * 0.25)
        else:
            # evade: maximize distance, prefer routes that keep options, and avoid obstacles
            score = (d_to_opp * 10) + (mo * 1.5) + (fn * 0.25)

        # deterministic tie-break: prefer moves that align with/outpace relative vector
        if dx == 0 and dy == 0:
            align = -0.05
        else:
            rvx, rvy = (nx - sx), (ny - sy)
            ovx, ovy = (nx - ox), (ny - oy)
            align = (rvx * (1 if ovx > 0 else (-1 if ovx < 0 else 0)) + rvy * (1 if ovy > 0 else (-1 if ovy < 0 else 0))) * 0.01
        score += align

        if best_score is None or (score > best_score):
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best