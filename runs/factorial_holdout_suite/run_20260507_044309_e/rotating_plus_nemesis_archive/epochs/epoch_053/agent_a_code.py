def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def manhattan(x, y, tx, ty):
        return abs(x - tx) + abs(y - ty)

    # Prefer resources where we're earlier than opponent; if tie, choose ones far from opponent's current row (sweep_rows counter).
    best = None
    best_key = None
    for rx, ry in resources:
        sd = manhattan(sx, sy, rx, ry)
        od = manhattan(ox, oy, rx, ry)
        race = od - sd  # higher is better: opponent farther than us
        key = (race, -sd, abs(ry - oy), -abs(rx - ox))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    # If all surrounding are blocked, fall back to staying.
    if not moves:
        return [0, 0]

    best_move = None
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nd = manhattan(nx, ny, tx, ty)
        sd = manhattan(sx, sy, tx, ty)
        od = manhattan(ox, oy, tx, ty)
        race_after = od - nd
        key = (-(nd), -(race_after), abs((nx - sx)) + abs((ny - sy)), -sd)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]