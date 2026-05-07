def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]
    if (sx, sy) in set(resources):
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def king_dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    best_score = None
    best_move = (0, 0)
    my_pos = (sx, sy)

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            nx, ny = sx, sy
        if (nx, ny) == my_pos and (dxm, dym) != (0, 0):
            continue

        score = -10**9
        for rx, ry in resources:
            myd = king_dist(nx, ny, rx, ry)
            opd = king_dist(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; then closer; then further from opponent.
            delta = opd - myd
            if delta < 0:
                val = -200 + delta  # likely lose
            else:
                val = 2000 + 20 * delta
            val += -myd
            val += 0.1 * (opd)
            # Small deterministic preference: favor resources in our forward direction (down/right from our start).
            val += 0.01 * (ry + rx)
            if val > score:
                score = val

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]