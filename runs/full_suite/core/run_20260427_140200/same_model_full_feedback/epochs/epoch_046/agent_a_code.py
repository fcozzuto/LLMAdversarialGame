def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    def pos_value(x, y):
        if not resources:
            # No known resources: move to contest opponent / centralize
            d1 = manh(x, y, ox, oy)
            dc = abs(x - (w - 1) / 2.0) + abs(y - (h - 1) / 2.0)
            return -(d1) - 0.05 * dc
        best = -10**9
        for rx, ry in resources:
            md = manh(x, y, rx, ry)
            od = manh(ox, oy, rx, ry)
            # Prefer targets where we are closer; discourage being far away.
            # Also penalize targets that opponent can reach much sooner.
            score = (od - md) - 0.18 * md
            if od + 1 < md:
                score -= 1.2 * (md - od)
            # Slight bias toward immediate capture likelihood.
            if md == 0:
                score += 3.0
            best = score if score > best else best
        # Encourage reducing gap to opponent to increase contest pressure.
        best += 0.03 * (manh(x, y, ox, oy) * -1)
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = pos_value(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    # If all moves invalid (shouldn't happen), stay.
    return [int(best_move[0]), int(best_move[1])]