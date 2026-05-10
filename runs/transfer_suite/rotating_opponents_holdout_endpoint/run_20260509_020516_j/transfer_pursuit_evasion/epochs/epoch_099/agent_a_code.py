def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    role = (observation.get("self_role") or "").lower()
    chasing = ("pursuer" in role) or ("catch" in role) or ("hunter" in role) or ("seeker" in role)
    if "evader" in role:
        chasing = False

    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    moves = []
    for dx in dxs:
        for dy in dys:
            if dx == 0 and dy == 0:
                pass
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            # Priority: capture quickly (or evade), then stability/orientation against zigzags
            md = abs(nx - ox) + abs(ny - oy)
            d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            # Predict opponent's likely direction using current relative vector sign (no history available)
            pvx = 0 if ox == sx else (1 if ox > sx else -1)
            pvy = 0 if oy == sy else (1 if oy > sy else -1)
            # If chasing, slightly prefer moving in the general direction of opponent movement bias
            bias = abs((nx - sx) - pvx) + abs((ny - sy) - pvy)
            # If evading, prefer opposite direction bias
            if chasing:
                score = (md, d2, bias)
            else:
                score = (-md, -d2, bias)
            # Deterministic tie-break: fixed order by dx,dy preference
            tie = (abs(dx), abs(dy), 0 if dx == 0 else (0 if dx == pvx else 1), 0 if dy == 0 else (0 if dy == pvy else 1))
            moves.append((score, tie, dx, dy))

    if not moves:
        return [0, 0]

    moves.sort(key=lambda t: (t[0], t[1]))
    return [int(moves[0][2]), int(moves[0][3])]