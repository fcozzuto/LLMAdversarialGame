def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("evasion" in r) or ("avoid" in r)

    self_is_evader = is_evader(observation.get("self_role", ""))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    turn = int(observation.get("turn_index", 0) or 0)

    best_move = (0, 0)
    best_score = None

    # Deterministic tie-break: prefer moves toward/away in x first, then y, then diagonals via ordering.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)

        # Primary objective: maximize distance as evader, minimize as pursuer.
        score = d if self_is_evader else -d

        # Secondary: avoid moving into a corner when evading; approach corner when pursuing.
        corner_targets = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        if self_is_evader:
            ct = min(dist2(nx, ny, cx, cy) for cx, cy in corner_targets)
            score += 0.01 * ct
        else:
            ct = max(dist2(nx, ny, cx, cy) for cx, cy in corner_targets)
            score += 0.01 * ct

        # Tertiary deterministic bias to break ties across symmetric moves.
        bias = (nx + ny) if (turn % 2 == 0) else (nx - ny)
        score += 1e-6 * bias

        if best_score is None or (score > best_score):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]