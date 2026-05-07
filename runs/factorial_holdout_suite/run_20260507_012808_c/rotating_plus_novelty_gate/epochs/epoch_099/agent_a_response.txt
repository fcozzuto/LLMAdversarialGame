def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or (0, 0)
    o = observation.get("opponent_position") or (0, 0)
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    sx, sy = clamp(sx, 0, w - 1), clamp(sy, 0, h - 1)
    ox, oy = clamp(ox, 0, w - 1), clamp(oy, 0, h - 1)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick target where we are relatively closer; tie-break: closer, then same-row/col bonus to counter row-sweeps
    best = None
    best_score = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        rel = do - ds  # higher means we're closer than opponent
        rc = (1 if sy == ty else 0) + (1 if sx == tx else 0)  # discourage walking past
        score = (rel * 1000) + rc * 5 - ds
        if best is None or score > best_score:
            best = (tx, ty)
            best_score = score

    tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Evaluate immediate move options; avoid stepping into obstacles
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        # prefer reducing our distance to target, while keeping advantage vs opponent
        nds = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        adv = nod - nds
        # small tie-break: keep moving along target direction
        prog = -(abs(nx - tx) + abs(ny - ty))
        val = adv * 1000 + prog - nds
        if best_val is None or val > best_val:
            best_val = val
            best_move = (nx - sx, ny - sy)

    # Ensure in {-1,0,1}
    mdx, mdy = best_move
    if mdx < -1: mdx = -1
    elif mdx > 1: mdx = 1
    if mdy < -1: mdy = -1
    elif mdy > 1: mdy = 1
    return [int(mdx), int(mdy)]