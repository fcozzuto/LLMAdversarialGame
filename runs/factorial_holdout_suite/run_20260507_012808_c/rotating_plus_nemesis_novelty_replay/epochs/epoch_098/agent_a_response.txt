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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def best_for(posx, posy):
        best = None
        bestv = -10**30
        for rx, ry in resources:
            myd = manh(posx, posy, rx, ry)
            opd = manh(ox, oy, rx, ry)
            if myd == 0:
                v = 10**9
            else:
                # Prefer resources we can reach no later than opponent, plus closeness.
                # opd - myd positive => advantage.
                v = (opd - myd) * 500 - myd * 5
            # small tie-break to keep deterministic preference
            v -= rx * 0.001 + ry * 0.0001
            if v > bestv:
                bestv = v
                best = (rx, ry)
        return bestv, best

    if not resources:
        # Simple corner-ward fallback
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    # Evaluate next move by greedy advantage against opponent to most contestable resource
    best_move = (0, 0)
    best_score = -10**30
    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        v, _ = best_for(nx, ny)
        # avoid moving away from current best target too much
        v -= manh(nx, ny, ox, oy) * 0.001
        if v > best_score:
            best_score = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]