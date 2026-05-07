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
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    best = None
    best_score = -10**18

    centerx, centery = w // 2, h // 2
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        # Prefer resources I'm closer to; strongly penalize those I'm slower on.
        # Also slightly prefer center-ish resources (helps with tie cases and stability).
        score = (opd - myd) * 2000 + (-(abs(rx - centerx) + abs(ry - centery)))
        if best is None or score > best_score or (score == best_score and (myd < best[0] or (myd == best[0] and myd != 0))):
            best_score = score
            best = (myd, rx, ry)

    _, tx, ty = best

    # Simple local "resource denial": if opponent is closer to my chosen target by enough, move to reduce that gap.
    my_to_t = manh(sx, sy, tx, ty)
    op_to_t = manh(ox, oy, tx, ty)
    if op_to_t < my_to_t - 1:
        # Move toward a different resource where I'm relatively advantaged.
        best2 = (my_to_t, tx, ty)
        best2_score = best_score
        for rx, ry in resources:
            myd = manh(sx, sy, rx, ry)
            opd = manh(ox, oy, rx, ry)
            score = (opd - myd) * 2000 + (-(abs(rx - centerx) + abs(ry - centery)))
            if score > best2_score:
                best2_score = score
                best2 = (myd, rx, ry)
        tx, ty = best2[1], best2[2]

    # Choose a move that reduces distance to (tx,ty) while avoiding obvious obstacle hits.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_dist = 10**9
    best_block = 10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        blocked = 1 if (nx, ny) in obstacles else 0
        d = manh(nx, ny, tx, ty)
        # Prefer non-blocked; then smallest distance; then prefer moves that also move away from opponent if close.
        if blocked == 0:
            if d < best_dist:
                best_dist = d; best_block = 0; best_move = (dx, dy)
            elif d == best_dist:
                opp_pen = manh(nx, ny, ox, oy)
                curr_pen = manh(sx + best_move[0], sy + best_move[1], ox, oy)
                if opp_pen > curr_pen:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]