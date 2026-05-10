def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in self_role) or ("evad" in opp_role and "evad" not in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def man(x, y):
        return abs(x - ox) + abs(y - oy)

    def center_bias(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return abs(x - cx) + abs(y - cy)

    best = None
    best_move = [0, 0]

    # One-step minimax: anticipate opponent's best response.
    # If pursuer: minimize worst-case distance after opponent moves.
    # If evader: maximize worst-case distance after opponent moves (i.e., avoid being cornered).
    opp_moves = []
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if valid(nx, ny):
            opp_moves.append((nx, ny))
    if not opp_moves:
        opp_moves = [(ox, oy)]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # If we move onto opponent, capture ends immediately in pursuer role (score win),
        # in evader role it's catastrophic (but capture is only awarded to pursuer).
        if pursuer and nx == ox and ny == oy:
            return [dx, dy]

        worst = None
        # Opponent will choose move that benefits them:
        # - if pursuer, opponent (evader) tries to maximize our distance.
        # - if evader, opponent (pursuer) tries to minimize our distance.
        for ax, ay in opp_moves:
            d = abs(nx - ax) + abs(ny - ay)
            val = d
            if worst is None:
                worst = val
            else:
                if pursuer:
                    if val > worst:
                        worst = val
                else:
                    if val < worst:
                        worst = val

        # Add small tie-breakers for robustness (center / obstacle avoidance already handled).
        # Use opposing bias depending on role.
        if pursuer:
            score = -1000 * worst - 2 * center_bias(nx, ny)
        else:
            score = 1000 * worst - 2 * center_bias(nx, ny)

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move