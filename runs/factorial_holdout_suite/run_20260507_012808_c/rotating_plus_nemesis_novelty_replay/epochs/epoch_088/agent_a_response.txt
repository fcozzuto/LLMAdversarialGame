def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 1 if sx < tx else (-1 if sx > tx else 0)
        dy = 1 if sy < ty else (-1 if sy > ty else 0)
        return [dx, dy]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        score = (opd - myd) * 10 - myd  # prefer resources I can reach earlier
        if score > best_score or (score == best_score and (rx < best[0] or (rx == best[0] and ry < best[1]))):
            best_score = score
            best = (rx, ry)

    tx, ty = best
    curd = manh(sx, sy, tx, ty)
    best_step = (0, 0)
    best_newd = curd + 10**6

    for dx, dy in deltas:
        nx = sx + dx; ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        nd = manh(nx, ny, tx, ty)
        if nd < best_newd or (nd == best_newd and (dx, dy) < best_step):
            best_newd = nd
            best_step = (dx, dy)

    if best_newd <= curd:
        return [int(best_step[0]), int(best_step[1])]
    return [0, 0]