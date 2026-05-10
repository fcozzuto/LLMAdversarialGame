def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("evasion" in role)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = moves[4]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)
        mob = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if valid(tx, ty):
                mob += 1
        # Deterministic tie-break by move order (first max/min encountered)
        score = (d if is_evader else -d) + (mob * (1 if is_evader else 0.5))
        if best_score is None:
            best_score, best_move = score, [dx, dy]
        else:
            if is_evader:
                if score > best_score:
                    best_score, best_move = score, [dx, dy]
            else:
                if score > best_score:
                    best_score, best_move = score, [dx, dy]
    return best_move