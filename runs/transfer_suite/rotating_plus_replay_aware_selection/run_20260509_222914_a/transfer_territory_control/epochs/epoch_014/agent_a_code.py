def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    try:
        sx, sy = int(sx), int(sy)
    except:
        sx, sy = 0, 0
    try:
        ox, oy = int(ox), int(oy)
    except:
        ox, oy = 0, 0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources") or []
    targets = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                targets.append((x, y))
    if not targets:
        targets = [(w // 2, h // 2)]

    tx, ty = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
    options = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)]
    best = None
    best_val = None
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_self = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(ox - nx) + abs(oy - ny)
        val = (d_self, -d_opp, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)
    return [best[0], best[1]]