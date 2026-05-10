def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = str(observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) or ("hunter" in role) or (not ("evader" in role or "runner" in role))

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        score = -dist2 if pursuer else dist2
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    if legal(sx + best_move[0], sy + best_move[1]):
        return [int(best_move[0]), int(best_move[1])]

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]