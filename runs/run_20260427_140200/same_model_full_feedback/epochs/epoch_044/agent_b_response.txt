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

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if resources:
        best = None
        myd0 = 10**9
        for rx, ry in resources:
            md = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Prefer close resources; avoid ones opponent is much closer to.
            score = md - 0.35 * od + (0.02 * (md + od))
            if best is None or score < best[0] or (score == best[0] and md < myd0):
                best = (score, md, rx, ry)
                myd0 = md
        _, _, tx, ty = best
        best_move = None
        best_val = 10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            my_next = dist(nx, ny, tx, ty)
            opp_next = dist(ox, oy, tx, ty)
            # Strongly minimize distance to chosen target; small "trap" if we reduce gap to it vs opponent.
            val = my_next - 0.25 * (my_next - opp_next)
            if best_move is None or val < best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        if best_move is not None:
            return [best_move[0], best_move[1]]

    # Fallback: any valid move that maximizes distance from opponent (deterministic tie-break).
    best_move = None
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = dist(nx, ny, ox, oy)
        if best_move is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]