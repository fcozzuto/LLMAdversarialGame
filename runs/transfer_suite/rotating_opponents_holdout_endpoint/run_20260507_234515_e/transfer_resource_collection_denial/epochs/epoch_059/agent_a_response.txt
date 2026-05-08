def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_target = None
    best_val = None
    for tx, ty in res:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Bias: avoid opponent's current row to counter row-sweeping
        row_pen = 0.7 if ty == oy else 0.0
        val = (sd - od) - row_pen
        if best_val is None or val < best_val or (val == best_val and (sd < man(sx, sy, best_target[0], best_target[1]))):
            best_val = val
            best_target = (tx, ty)

    tx, ty = best_target
    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # Prefer moves that improve the race to the chosen target; deterministic tiebreak order
    order = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ord_idx = {m: i for i, m in enumerate(order)}
    best_move = None
    best_move_val = None
    for dx, dy, nx, ny in cand:
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        row_pen = 0.7 if ny == oy else 0.0
        val = (sd - od) - row_pen
        if best_move_val is None or val < best_move_val or (val == best_move_val and ord_idx[(dx, dy)] < ord_idx[(best_move[0], best_move[1])]):
            best_move_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]