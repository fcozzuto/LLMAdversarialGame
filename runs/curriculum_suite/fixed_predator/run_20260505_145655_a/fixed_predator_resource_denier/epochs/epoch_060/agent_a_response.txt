def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0

    def cell_value(px, py):
        best = None
        for rx, ry in resources:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            # deny: prefer resources opponent is closer to; add penalty for our distance
            v = (od - sd) * 10 - sd
            # slight preference toward center for stability
            v += -(((rx - cx0) * (rx - cx0) + (ry - cy0) * (ry - cy0)) * 1e-4)
            # tiny tiebreak: avoid letting opponent get too near our cell
            v += -0.05 * man(px, py, ox, oy)
            if best is None or v > best:
                best = v
        return best

    best_move = (0, 0)
    best_score = None
    # Deterministic tie-breaking order: favor straight/diagonal toward target implicitly via score.
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            sc = cell_value(nx, ny)
            if best_score is None or sc > best_score:
                best_score = sc
                best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]