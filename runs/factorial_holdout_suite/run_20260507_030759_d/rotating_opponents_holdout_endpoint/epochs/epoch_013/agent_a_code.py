def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(a, b, c, d): return abs(a - c) + abs(b - d)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = [0, 0]
    best_score = -10**18

    if not inb(sx, sy):
        return [0, 0]

    # If no resources, drift toward center but don't walk into obstacles
    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            # prefer moves that reduce Euclidean distance squared to center
            sc = -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty))
            if sc > best_score:
                best_score = sc
                best_move = [dx, dy]
        return best_move

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Depth-1 lookahead: choose move that maximizes opponent-self advantage on the best reachable resource now
        move_best_adv = -10**18
        move_best_self = 10**18
        for rx, ry in resources:
            self_d1 = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            adv = opp_d - self_d1  # positive => we arrive sooner (or later if negative)
            # tie-break: prefer closer self distance for the chosen advantage
            if adv > move_best_adv or (adv == move_best_adv and self_d1 < move_best_self):
                move_best_adv = adv
                move_best_self = self_d1

        # Also add a small term to avoid letting opponent get strictly better advantage next
        opp_move_pressure = 0
        # Since we don't control opponent, use current opp distances implicitly; penalize very close to opponent to reduce contest sweeps
        dist_opp = md(nx, ny, ox, oy)
        opp_move_pressure = -0.05 * max(0, 6 - dist_opp)

        sc = move_best_adv * 10 - move_best_self + opp_move_pressure
        if sc > best_score:
            best_score = sc
            best_move = [dx, dy]

    return best_move