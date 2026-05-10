def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles", []) or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = str(observation.get("self_role", "") or "").lower()
    evader = "evader" in role

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    best_score = None

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        score = dist if evader else -dist
        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score

    if best is not None:
        return best

    # If all are blocked, stay if possible else move to first valid neighbor.
    if in_bounds(sx, sy):
        return [0, 0]
    for dx, dy in moves[:-1]:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny):
            return [dx, dy]
    return [0, 0]