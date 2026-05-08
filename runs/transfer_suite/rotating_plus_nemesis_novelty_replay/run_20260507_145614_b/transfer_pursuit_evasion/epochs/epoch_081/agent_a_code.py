def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chaser" in self_role) or ("tag" in self_role)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obst_penalty(x, y):
        # Prefer keeping distance from obstacles (avoid stepping into them by large penalty)
        if (x, y) in obst:
            return 10**8
        best = 10**9
        for bx, by in obst:
            d = dist2(x, y, bx, by)
            if d < best:
                best = d
                if best == 0:
                    break
        if best == 10**9:
            return 0
        return 50.0 / (1.0 + best)  # smaller best => larger penalty

    best_score = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        d = dist2(nx, ny, ox, oy)
        # Pursuer: minimize distance; Evader: maximize distance
        base = -d if is_pursuer else d

        # Obstacle-aware and boundary-safety (soft)
        pen = obst_penalty(nx, ny)
        edge = 0
        if nx == 0 or nx == w - 1:
            edge += 1
        if ny == 0 or ny == h - 1:
            edge += 1
        # Keep deterministic tie-breakers: diagonal preference then larger distance (for evader) or smaller (for pursuer)
        diag = 1 if (dx != 0 and dy != 0) else 0

        score = base - pen - edge * (0.5 if is_pursuer else 0.2) + diag * (0.01 if is_pursuer else 0.02)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]