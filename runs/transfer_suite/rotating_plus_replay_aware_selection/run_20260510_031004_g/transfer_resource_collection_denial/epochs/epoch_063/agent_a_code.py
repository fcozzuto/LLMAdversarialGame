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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def clamp(x, lo, hi):
        if x < lo: return lo
        if x > hi: return hi
        return x

    cand = []
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds <= do:
            # Prefer resources we can reach no later than opponent; break ties by larger margin, then closer to us
            cand.append((do - ds, -ds, -rx, -ry, rx, ry))
        else:
            # Fallback pool for when opponent is closer: minimize our distance but prefer slightly farther opponent
            cand.append((-(ds - do), -ds, -do, -rx, -ry, rx, ry))

    cand.sort(reverse=True)
    rx, ry = cand[0][4], cand[0][5]

    best_move = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx = clamp(sx + dx, 0, w - 1)
            ny = clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obstacles:
                continue
            # Score move by reduction in our distance to target; small penalty for increasing opponent advantage
            before = cheb(sx, sy, rx, ry)
            after = cheb(nx, ny, rx, ry)
            opp_before = cheb(ox, oy, rx, ry)
            opp_after = cheb(ox, oy, rx, ry)  # opponent assumed unchanged this turn
            move_score = (before - after) * 100 - after - opp_before * 0.001 - (dx * dx + dy * dy) * 0.01
            if best_move is None or move_score > best_move[0]:
                best_move = (move_score, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]