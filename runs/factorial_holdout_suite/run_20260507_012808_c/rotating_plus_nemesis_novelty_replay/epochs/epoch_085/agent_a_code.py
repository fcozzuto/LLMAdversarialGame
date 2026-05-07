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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    best = None
    best_key = None
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        # Prefer resources we're at least as close to (or closest overall); then reduce our distance.
        # Deterministic tie-break: lower (rx,ry).
        key = (-(1 if myd <= opd else 0), myd - opd, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = manh(nx, ny, rx, ry)
        # If we can reach the target this turn, prioritize; else greedy decrease distance with small preference to
        # not move away from opponent's closer resources.
        hit = 1 if nd == 0 else 0
        mv_key = (-hit, nd, abs(ox - nx) + abs(oy - ny), dx, dy)
        if best_move_key is None or mv_key < best_move_key:
            best_move_key = mv_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]