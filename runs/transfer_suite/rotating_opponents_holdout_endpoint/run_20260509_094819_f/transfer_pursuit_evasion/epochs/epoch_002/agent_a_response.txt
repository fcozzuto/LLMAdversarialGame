def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    x, y = int(self_pos[0]), int(self_pos[1])
    ox, oy = int(opp_pos[0]), int(opp_pos[1])
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(px), int(py)) for px, py in obstacles)

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("purs" in opp_role and "evad" not in self_role)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def corner_score(nx, ny):
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        return max(abs(nx - cx) + abs(ny - cy) for cx, cy in corners)

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        man = abs(nx - ox) + abs(ny - oy)
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)

        # Count how constrained the next position is (fewer valid neighbors is worse)
        neigh = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                neigh += 1

        if is_pursuer:
            # Primary: minimize distance; Secondary: avoid being trapped; Tertiary: prefer moves that align with opponent.
            if nx == ox and ny == oy:
                score = 10**9
            else:
                score = (-d2) * 1000 - man * 10 + neigh
        else:
            # Primary: maximize distance; Secondary: prefer moving away and towards corners; avoid being trapped.
            if nx == ox and ny == oy:
                score = -10**9
            else:
                score = (d2) * 1000 + man * 10 + corner_score(nx, ny) + neigh

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]