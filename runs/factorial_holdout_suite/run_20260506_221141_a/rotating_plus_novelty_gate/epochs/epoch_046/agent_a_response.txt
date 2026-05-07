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

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick resource where we have the largest "race advantage" (opponent farther than us).
    best = None
    best_key = None
    for rx, ry in resources:
        cd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        key = (od - cd, -cd, -manh(ox, oy, sx, sy))
        if best is None or key > best_key:
            best, best_key = (rx, ry), key
    tx, ty = best

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best_step = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        # Score step: get closer to target; if still losing the race to target, reduce damage and
        # also try to move toward where opponent is (shadow pursuit to intercept).
        d_self = manh(nx, ny, tx, ty)
        d_opp = manh(ox, oy, tx, ty)
        d_opp_to_us = manh(nx, ny, ox, oy)
        step_key = ((d_opp - d_self), -d_self, -d_opp_to_us)
        if best_score is None or step_key > best_score:
            best_score = step_key
            best_step = [dx, dy]

    if best_score is None:
        return [0, 0]
    return best_step