def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (0, 1), (1, 0), (0, -1),
             (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    if not resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best_res = None
    best_key = None
    for rx, ry in resources:
        myd = md(sx, sy, rx, ry)
        opd = md(ox, oy, rx, ry)
        key = (opd - myd, -myd, rx, ry)  # prefer being closer than opponent; then closer overall
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res

    chosen = (0, 0)
    chosen_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd2 = md(nx, ny, rx, ry)
        opd2 = md(nx, ny, ox, oy)
        target_pick = 1 if (nx, ny) == (rx, ry) else 0
        oppd_target = md(ox, oy, rx, ry)
        # deterministic scoring: take target if possible, otherwise move to reduce my distance
        key = (target_pick, -(myd2), -(opd2 - md(ox, oy, ox, oy)), -(oppd_target - myd2), rx, ry, nx, ny)
        if chosen_key is None or key > chosen_key:
            chosen_key = key
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]