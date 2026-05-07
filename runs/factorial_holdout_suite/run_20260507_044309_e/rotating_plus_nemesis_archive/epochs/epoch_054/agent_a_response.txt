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

    # Pick resource with best "race": opponent distance minus our distance.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = manhattan(sx, sy, rx, ry)
        od = manhattan(ox, oy, rx, ry)
        race = od - sd  # higher => we are (or get there) earlier
        # Mild bias: if we're tied, prefer targets that progress away from opponent and toward our corner.
        prog = (rx + ry) if (sx + sy) <= (ox + oy) else (w - 1 - rx + h - 1 - ry)
        key = (race, -sd, -abs(ry - oy), -abs(rx - ox), -prog)
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
    if not moves:
        moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                 if 0 <= sx + dx < w and 0 <= sy + dy < h]

    # Greedy: minimize our distance to target; break ties by maximizing distance from opponent (denier pressure).
    best_move = None
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_to_t = manhattan(nx, ny, tx, ty)
        d_from_o = manhattan(nx, ny, ox, oy)
        # Also add small penalty for stepping into "late" region relative to opponent's current advantage.
        race_after = manhattan(ox, oy, tx, ty) - d_to_t
        mkey = (race_after, -d_from_o, -((d_to_t == 0) * 1), -abs((nx + ny) - (tx + ty)))
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]