def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(obstacles_list) if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    # Select a resource we can arrive before opponent (margin), else minimize opponent advantage.
    best_score = None
    best_t = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        margin = do - ds  # positive => we are closer
        # Prefer diagonal/straight-ish paths by slight tie-break on ds.
        # Also bias toward staying away from the opponent when we can't win the race.
        opp_bias = 0.0 if margin > 0 else (0.3 * (abs(rx - ox) + abs(ry - oy)))
        score = (margin, -ds - opp_bias, rx, ry)
        if best_score is None or score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Greedy toward target; if tie, prefer moves that keep opponent farther.
        d_self = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # Estimate opponent racing after our move: approximate with their current distance delta (conservative).
        est_race = (d_opp - d_self)
        val = (-d_self, -est_race, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]