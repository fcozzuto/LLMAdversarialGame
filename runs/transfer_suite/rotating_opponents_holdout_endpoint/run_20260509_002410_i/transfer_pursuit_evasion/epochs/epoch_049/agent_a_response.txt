def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in self_role) or (self_role == "evader")

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obstacle_pressure(x, y):
        # penalize being close to obstacles to avoid getting wedged
        # (deterministic, small computation)
        pen = 0
        for (ox2, oy2) in obstacles:
            md = abs(x - ox2) + abs(y - oy2)
            if md == 0:
                return 10**9
            if md == 1:
                pen += 3
            elif md == 2:
                pen += 1
        return pen

    # Optional: bias evader away from the pursuer's corner trend by preferring runs
    # toward farther edge; helps vs corner evasion opponent archetype.
    def edge_bias(x, y):
        # farther from nearest corner is better for evader; for pursuer, prefer nearer
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        dmin = min(manh(x, y, cx, cy) for (cx, cy) in corners)
        return -dmin if not is_evader else dmin

    best_score = None
    best_move = [0, 0]
    # Tie-break deterministically: prefer larger x then larger y
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = manh(nx, ny, ox, oy)
        obst = obstacle_pressure(nx, ny)
        if is_evader:
            score = d * 100 - obst * 10 + edge_bias(nx, ny)
        else:
            score = (-d) * 100 - obst * 10 - edge_bias(nx, ny)

        if best_score is None or score > best_score or (score == best_score and (nx > sx + best_move[0] or (nx == sx + best_move[0] and ny > sy + best_move[1]))):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]