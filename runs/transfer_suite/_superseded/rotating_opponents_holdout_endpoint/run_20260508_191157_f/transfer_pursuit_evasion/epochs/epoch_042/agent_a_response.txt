def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    role = observation.get("self_role", "pursuer")
    env = observation.get("environment_name", "")
    if env != "pursuit_evasion":
        return [0, 0]

    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if role == "pursuer":
        # immediate capture if possible
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny) and (nx, ny) == (ox, oy):
                return [dx, dy]

    my_move_is_max = (role != "pursuer")  # if evader, maximize distance; if pursuer, minimize
    best = None
    best_move = (0, 0)

    # Two-ply: my move, then opponent greedy response
    for dx1, dy1 in deltas:
        x1, y1 = sx + dx1, sy + dy1
        if not ok(x1, y1):
            continue

        # Opponent move
        if role == "pursuer":
            # opponent evades greedily: maximize distance from (x1,y1)
            best_opp = None
            for dx2, dy2 in deltas:
                x2, y2 = ox + dx2, oy + dy2
                if not ok(x2, y2):
                    continue
                d = dist(x1, y1, x2, y2)
                score = d
                if best_opp is None or score > best_opp:
                    best_opp = score
        else:
            # opponent pursues greedily: minimize distance to (x1,y1)
            best_opp = None
            for dx2, dy2 in deltas:
                x2, y2 = ox + dx2, oy + dy2
                if not ok(x2, y2):
                    continue
                d = dist(x1, y1, x2, y2)
                score = d
                if best_opp is None or score < best_opp:
                    best_opp = score

        # If capture possible at end of my move
        if role == "pursuer" and (x1, y1) == (ox, oy):
            value = -10**9
        else:
            value = best_opp
            # Tie-breakers: favor moving toward/away from opponent; avoid staying if not needed
            dir1 = dist(x1, y1, ox, oy)
            dir0 = dist(sx, sy, ox, oy)
            approach = -1 if role == "pursuer" else 1
            value = value + approach * 0.001 * (dir1 - dir0) - 0.0005 * (dx1 == 0 and dy1 == 0)

        if best is None:
            best = value
            best_move = (dx1, dy1)
        else:
            if my_move_is_max:
                if value > best:
                    best = value
                    best_move = (dx1, dy1)
            else:
                if value < best:
                    best = value
                    best_move = (dx1, dy1)

    dx, dy = best_move
    return [int(dx), int(dy)]