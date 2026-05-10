def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If we can safely win a resource race, prioritize it.
    # Otherwise, move to a cell that blocks/denies the opponent's likely route:
    # choose a resource whose distance-to-opponent is small, and move toward it to contest.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # race_margin: positive means we arrive earlier or tie
        race_margin = od - sd
        # also prefer resources closer to center-ish for better future options
        center_bonus = -abs(rx - (w - 1) / 2) - abs(ry - (h - 1) / 2)
        # key favors winning race; tie-break: smaller self distance; then center-ish
        key = (1 if race_margin > 0 else 0, race_margin, -sd, center_bonus, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # If we aren't ahead for the chosen target, add a small contesting rule:
    # contest the best resource by opponent reach if available.
    if cheb(sx, sy, tx, ty) >= cheb(ox, oy, tx, ty):
        best2 = None
        best2_key = None
        for rx, ry in resources:
            od = cheb(ox, oy, rx, ry)
            sd = cheb(sx, sy, rx, ry)
            # prioritize resources the opponent can reach sooner; but still keep them reachable by us reasonably
            k2 = (-od, sd, -abs(rx - sx) - abs(ry - sy), -rx, -ry)
            if best2_key is None or k2 > best2_key:
                best2_key = k2
                best2 = (rx, ry)
        tx, ty = best2

    dx = tx - sx
    dy = ty - sy

    step_x = 0
    if dx > 0: step_x = 1
    elif dx < 0: step_x = -1
    step_y = 0
    if dy > 0: step_y = 1
    elif dy < 0: step_y = -1

    # Avoid stepping into obstacles if possible (try axis-aligned alternatives).
    nx, ny = sx + step_x, sy + step_y
    if (nx, ny) in obstacles:
        # try x only
        if (sx + step_x, sy) not in obstacles and step_x != 0:
            return [step_x, 0]
        # try y only
        if (sx, sy + step_y) not in obstacles and step_y != 0:
            return [0, step_y]
        # try staying
        return [0, 0]
    return [step_x, step_y]