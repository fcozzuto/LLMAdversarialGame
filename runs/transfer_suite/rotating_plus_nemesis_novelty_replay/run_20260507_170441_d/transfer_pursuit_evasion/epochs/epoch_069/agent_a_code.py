def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    self_role = (observation.get("self_role", "") or "").lower()
    evader = ("evader" in self_role) or ("runner" in self_role)

    def mdist(x, y, a, b):
        return abs(x - a) + abs(y - b)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    curd = mdist(sx, sy, ox, oy)

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        nd = mdist(nx, ny, ox, oy)

        # Reward distancing (evader) or approach (pursuer). Add obstacle avoidance by penalizing adjacency.
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                x2, y2 = nx + ax, ny + ay
                if (x2, y2) in obstacles:
                    adj_obs += 1

        if evader:
            score = (nd - curd) + 0.15 * nd - 0.25 * adj_obs
        else:
            score = -(nd - curd) - 0.15 * nd - 0.25 * adj_obs

        # Deterministic tie-break: larger score, then lexicographically smaller move (dx,dy).
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]