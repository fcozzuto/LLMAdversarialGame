def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    selfT = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opT = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unT = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    cx, cy = w // 2, h // 2
    self_count = int(observation.get("self_territory_count", len(selfT)))
    op_count = int(observation.get("opponent_territory_count", len(opT)))
    losing = self_count < op_count

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def step_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        if (nx, ny) in selfT:
            status = 0
        elif (nx, ny) in opT:
            status = 2
        else:
            status = 1 if (nx, ny) in unT else 0

        sdist_to_center = dist2(nx, ny, cx, cy)
        sdist_to_op = dist2(nx, ny, ox, oy)

        if losing:
            if status == 2:
                score = 1200 - sdist_to_op
            elif status == 1:
                score = 220 - sdist_to_op + 40 * (1 if dist2(nx, ny, cx, cy) < dist2(sx, sy, cx, cy) else 0)
            else:
                score = -50 + 5 * (-(sdist_to_center))
        else:
            if status == 1:
                score = 900 - sdist_to_center
            elif status == 2:
                score = 450 - sdist_to_op
            else:
                score = 30 - sdist_to_center

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]