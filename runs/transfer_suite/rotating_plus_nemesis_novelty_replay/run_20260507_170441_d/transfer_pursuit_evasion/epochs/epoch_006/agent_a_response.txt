def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    self_role = (observation.get("self_role", "") or "").lower()
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obs.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obs
    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def degree(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    is_pursuer = ("pursuer" in self_role) or ("tag" in self_role) or ("chaser" in self_role) or ("hunter" in self_role)
    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = d2(nx, ny, ox, oy)
        deg = degree(nx, ny)

        # Additional shaping: discourage moves that make opponent's immediate escape easier.
        # Estimate by counting opponent's valid neighbor cells after we move (opponent moves next).
        opp_escape = 0
        for odx, ody in moves:
            ex, ey = ox + odx, oy + ody
            if valid(ex, ey):
                # If we are closer after their escape, it's better for us if we're pursuer.
                opp_escape += 1

        # If pursuer: minimize distance, break ties by maximizing own mobility.
        # If evader: maximize distance, break ties by minimizing opponent escape options.
        if is_pursuer:
            score = (-dist, -opp_escape, -(-deg))  # prefer smaller dist, then reduce opp options, then higher deg
        else:
            score = (dist, opp_escape, deg)  # prefer larger dist, then reduce opp options, then higher deg

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]