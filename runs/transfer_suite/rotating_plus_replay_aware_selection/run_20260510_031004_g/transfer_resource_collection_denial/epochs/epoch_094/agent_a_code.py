def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # Pick a target: favor contesting where we are faster; otherwise go for nearest we can reach.
    best = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        advantage = opp_d - my_d  # positive => we are faster/at least not slower
        # Deterministic tie-breaks: higher advantage, smaller my_d, then lexicographic cell.
        key = (advantage, -my_d, -(abs(sx - rx) + abs(sy - ry)), rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    _, (tx, ty) = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        my_next = cheb(nx, ny, tx, ty)
        # Prefer reducing our distance; if tied, prefer larger immediate lead over opponent; avoid dithering by slight movement penalty.
        opp_now = cheb(ox, oy, tx, ty)
        move_pen = abs(dx) + abs(dy)
        key = (-my_next, (opp_now - my_next), -move_pen, dx, dy)
        if bestm is None or key > bestm[0]:
            bestm = (key, (dx, dy))

    if bestm is None:
        return [0, 0]
    return [int(bestm[1][0]), int(bestm[1][1])]