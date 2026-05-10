def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    resources = []
    for p in observation.get("resources") or []:
        try:
            resources.append((p[0], p[1]))
        except Exception:
            pass

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(ax, ay, bx, by):
        return (ax - bx if ax >= bx else bx - ax) + (ay - by if ay >= by else by - ay)

    if resources:
        best_t = None
        for rx, ry in resources:
            myd = man(x, y, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Prefer resources where we are relatively closer; tie-break by absolute distance and position.
            key = (myd - opd, myd, rx, ry)
            if best_t is None or key < best_t[0]:
                best_t = (key, (rx, ry))
        tx, ty = best_t[1]
    else:
        tx, ty = w // 2, h // 2

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        dtar = man(nx, ny, tx, ty)
        dop = man(nx, ny, ox, oy)
        # Primary: get closer to chosen target. Secondary: avoid moves that allow opponent to get much closer.
        score = (dtar, dop - man(ox, oy, tx, ty), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move