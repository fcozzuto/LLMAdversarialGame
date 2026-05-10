def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                blocked.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H:
                res.append((x, y))

    cx = (W - 1) // 2
    cy = (H - 1) // 2

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_sc = -10**18

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H:
            continue
        if (nx, ny) in blocked:
            continue

        d_opp = manh(nx, ny, ox, oy)
        sc = 0
        if (nx, ny) == (ox, oy):
            sc -= 10**6
        sc -= d_opp * 5

        if res:
            d_res = min(manh(nx, ny, rx, ry) for rx, ry in res)
            sc -= d_res * 2
        else:
            sc -= manh(nx, ny, cx, cy)

        # Prefer moving into cells closer to center if no resources
        sc += -manh(nx, ny, cx, cy) if not res else 0

        # Small deterministic tie-break: lex order via fixed iteration
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best