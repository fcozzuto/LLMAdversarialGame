def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # Prefer resources that we can reach sooner while staying further from opponent.
    # Also bias toward moving toward our starting corner half to counter row-sweeps.
    bias_x = 1 if sx < (W - 1) / 2 else -1
    bias_y = 1 if sy < (H - 1) / 2 else -1

    def best_for_pos(px, py):
        best = None
        for x, y in res:
            d1 = abs(x - px) + abs(y - py)
            d2 = abs(x - ox) + abs(y - oy)
            # Anticipate our progress; reward being closer than opponent.
            # Tie-break toward lower distance and toward our half.
            bx = (x - (0 if bias_x == 1 else W - 1)) * bias_x
            by = (y - (0 if bias_y == 1 else H - 1)) * bias_y
            score = ((d1 - 1.12 * d2), d1, -(bx + by))
            if best is None or score < best:
                best = score
        return best

    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        val = best_for_pos(nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]