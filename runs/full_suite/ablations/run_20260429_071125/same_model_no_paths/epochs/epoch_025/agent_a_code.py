def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def obstacle_pressure(x, y):
        # small penalty if target sits adjacent to obstacles (harder path)
        cnt = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in blocked:
                    cnt += 1
        return cnt

    # Strategic target: maximize capture advantage (how much closer we are than opponent),
    # with mild preference for being closer overall.
    best_t = None
    best_score = -10**9
    for x, y in resources:
        d_us = cheb(sx, sy, x, y)
        d_op = cheb(ox, oy, x, y)
        adv = d_op - d_us  # positive means we're closer
        score = 10 * adv - 2 * d_us - 3 * obstacle_pressure(x, y)
        if score > best_score:
            best_score = score
            best_t = (x, y)

    if best_t is None:
        # No resources: move to a deterministic safe-ish point toward center while avoiding obstacles
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_t

    # Choose move that greedily improves distance to target; if tie, improve capture advantage vs opponent.
    cur_d = cheb(sx, sy, tx, ty)
    cur_adv = cheb(ox, oy, tx, ty) - cur_d
    chosen = (0, 0)
    best = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d2 = cheb(nx, ny, tx, ty)
        adv2 = cheb(ox, oy, tx, ty) - d2
        # slight anti-stall: prefer decreasing distance; also discourage moving away.
        score = -3 * (d2 - cur_d) + 2 * (adv2 - cur_adv) - 0.1 * obstacle_pressure(nx, ny)
        if score > best:
            best = score
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]