def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) not in obstacles:
            resources.append((rx, ry))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    # Pick a target that we can reach sooner (or that denies opponent).
    best = None
    best_key = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        key = (opd - myd, -abs(myd - opd), -myd, -abs(rx - ox) - abs(ry - oy))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    current_opd = man(ox, oy, tx, ty)
    current_myd = man(sx, sy, tx, ty)

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, tx, ty)
        # Prefer arriving earlier than opponent at the target, and also reduce opponent's progress.
        val = 0
        val += 3 * (current_opd - myd)  # deny opponent by shrinking our distance
        val += -2 * max(0, myd - current_opd)  # avoid getting behind
        val += -abs(myd - current_opd)  # tighten race
        # Mild intercept: move closer to where opponent is going (towards our chosen target).
        oppd_from_move = man(ox, oy, tx, ty)
        val += -0.5 * abs(oppd_from_move - (myd + 1))
        # Small tie-break: go toward target generally
        val += -0.1 * myd

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]