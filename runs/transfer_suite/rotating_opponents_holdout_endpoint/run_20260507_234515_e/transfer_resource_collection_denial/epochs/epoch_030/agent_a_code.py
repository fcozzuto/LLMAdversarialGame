def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    if not resources:
        tx, ty = w - 1, 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        for ddx, ddy in ((dx, dy), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1), (0, 0)):
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [ddx, ddy]
        return [0, 0]

    best = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        adv = od - sd  # >0 means we are closer in steps
        # Strongly prefer states where we can likely take first; then minimize our distance.
        score = (1 if adv >= 0 else -1) * 1000 + (sd * 1) + (-(adv) * 2 if adv >= 0 else adv * 3)
        tiebreak = (rx + 31 * ry)  # deterministic stable ordering
        cand = (score, sd, tiebreak, rx, ry)
        if best is None or cand < best:
            best = cand

    _, _, _, tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    moves = []
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            nx, ny = sx + ddx, sy + ddy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                dist = abs(tx - nx) + abs(ty - ny)
                closer = 0
                curd = abs(tx - sx) + abs(ty - sy)
                if dist < curd:
                    closer = 1
                # Prefer exact greedy direction, then closer to target, then lexicographic determinism.
                greedy_bonus = 1 if ddx == dx and ddy == dy else 0
                moves.append((-(greedy_bonus * 10 + closer), dist, ddx, ddy))
    moves.sort()
    return [moves[0][2], moves[0][3]] if moves else [0, 0]