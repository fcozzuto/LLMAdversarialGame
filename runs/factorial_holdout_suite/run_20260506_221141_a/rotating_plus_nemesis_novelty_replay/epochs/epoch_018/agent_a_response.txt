def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
             (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < gw and 0 <= y < gh and (x, y) not in obs

    # Opponent archetype: sweep_rows -> prioritize resources far in y from opponent row.
    ALPHA = 2.0   # row separation weight
    BETA = 1.5    # competition weight

    def eval_pos(x, y):
        best = None
        for rx, ry in resources:
            ds = abs(rx - x) + abs(ry - y)
            do = abs(rx - ox) + abs(ry - oy)
            # Lower is better: advance to a resource, prefer different row than opponent, and beat their proximity.
            score = ds - ALPHA * abs(ry - oy) + BETA * (ds - do)
            if best is None or score < best:
                best = score
        return best if best is not None else 10**9

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = eval_pos(nx, ny)
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]