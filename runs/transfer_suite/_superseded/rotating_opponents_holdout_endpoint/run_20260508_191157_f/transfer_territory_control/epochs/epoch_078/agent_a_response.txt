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

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    oppT = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            oppT.add((int(p[0]), int(p[1])))

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                unclaimed.append((x, y))

    cx, cy = w // 2, h // 2
    if unclaimed:
        # Prefer cells that are closer to us than opponent, and also a bit toward center.
        best = None
        bestv = None
        for x, y in unclaimed:
            dself = abs(x - sx) + abs(y - sy)
            dopp = abs(x - ox) + abs(y - oy)
            center_bias = (abs(x - cx) + abs(y - cy)) * 0.01
            v = ((dopp - dself), -(-dself), center_bias, x, y)
            if best is None or v < bestv:
                best = (x, y)
                bestv = v
        tx, ty = best
    else:
        tx, ty = cx, cy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    bestm = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        step_to_target = abs(tx - nx) + abs(ty - ny) - (abs(tx - sx) + abs(ty - sy))
        # Slightly prefer stepping into opponent territory if it helps advance.
        flip_bonus = -0.15 if (nx, ny) in oppT else 0.0
        # Keep some momentum away from obstacles by penalizing staying if stuck.
        stuck_penalty = 0.02 if (dx == 0 and dy == 0) else 0.0
        score = (dist, abs(dx) + abs(dy), step_to_target, stuck_penalty + (-flip_bonus))
        if best_score is None or score < best_score:
            best_score = score
            bestm = [dx, dy]

    dx, dy = int(bestm[0]), int(bestm[1])
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [dx, dy]