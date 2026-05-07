def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    ALPHA = 1.25  # prefer positions closer to a resource than opponent
    BETA = 0.55   # avoid being too close to opponent near contested resources
    GAMMA = 0.10  # tiny preference toward resources far from opponent row (anti-sweep)
    EPS = 1e-9

    def best_score(x, y):
        best = -1e18
        for rx, ry in resources:
            ds = abs(rx - x) + abs(ry - y)
            do = abs(rx - ox) + abs(ry - oy)
            # Value increases when we are closer than opponent; lower ds and higher delta help.
            val = (ALPHA * (do - ds)) - ds * 0.03 + GAMMA * abs(ry - oy)
            # If opponent is adjacent to this resource and we get close too, it may "deny" effectively.
            opp_to_res = abs(rx - ox) + abs(ry - oy)
            if opp_to_res <= 2:
                val -= BETA * (abs(rx - x) + abs(ry - y))
            if val > best:
                best = val
        # Encourage progress by preferring states that reduce our nearest resource distance.
        nearest = min(abs(rx - x) + abs(ry - y) for rx, ry in resources)
        return best - 0.01 * nearest

    best_move = [0, 0]
    best_val = -1e18

    # Deterministic tie-breaking: prefer smallest dx, then dy, in listed order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = best_score(nx, ny)
        if v > best_val + EPS:
            best_val = v
            best_move = [dx, dy]

    return best_move