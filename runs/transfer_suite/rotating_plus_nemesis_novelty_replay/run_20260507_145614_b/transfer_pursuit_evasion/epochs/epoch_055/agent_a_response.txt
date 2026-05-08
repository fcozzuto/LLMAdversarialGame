def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    srole = (observation.get("self_role") or "").lower()
    orole = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in srole) or ("evasion" in srole) or (("evader" in orole or "evasion" in orole) and ("pursuer" not in srole))

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    phase = int(observation.get("turn_index", 0) or 0) % 3
    dirs = dirs[phase:] + dirs[:phase]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    best_moves = []

    # Greedy one-step lookahead (deterministic): prioritize moving away/toward opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)

        # Small obstacle-aware bias: prefer moves that keep mobility (avoid getting trapped).
        mob = 0
        for adx, ady in dirs:
            tx, ty = nx + adx, ny + ady
            if ok(tx, ty):
                mob += 1

        # Deterministic score: evader maximizes distance; pursuer minimizes distance.
        # Tie-break by mobility, then by lexicographic move order (from dirs).
        score = (-d, mob) if is_evader else (d, mob)

        if best is None:
            best = score
            best_moves = [(dx, dy)]
        else:
            if is_evader:
                if score[0] < best[0] or (score[0] == best[0] and score[1] > best[1]):
                    best = score
                    best_moves = [(dx, dy)]
                elif score[0] == best[0] and score[1] == best[1]:
                    best_moves.append((dx, dy))
            else:
                if score[0] < best[0] or (score[0] == best[0] and score[1] > best[1]):
                    best = score
                    best_moves = [(dx, dy)]
                elif score[0] == best[0] and score[1] == best[1]:
                    best_moves.append((dx, dy))

    if not best_moves:
        return [0, 0]
    # Deterministic tie-break: pick the earliest move in dirs order among best_moves.
    for mv in dirs:
        if mv in best_moves:
            return [int(mv[0]), int(mv[1])]
    return [0, 0]