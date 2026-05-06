def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    rlist = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                rlist.append((x, y))
    if not rlist:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                return [dx, dy]
        return [0, 0]

    # Advantage: prefer states where we can reach a resource sooner than opponent.
    alpha = 0.9
    beta = 0.25  # small penalty for being too close to opponent
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        oppd = md(ox, oy, nx, ny)
        # For each candidate next state, pick the resource with best "advantage"
        # (lowest my-advantage gap).
        cur_best = None
        for rx, ry in rlist:
            md_self = md(nx, ny, rx, ry)
            md_opp = md(ox, oy, rx, ry)
            # Lower is better for us; but we convert to a max score later.
            # Encourage taking resources opponent is relatively far from.
            gap = md_self - alpha * md_opp
            val = gap + beta * (1 if oppd <= 1 else 0)  # tiny safety shaping
            if cur_best is None or val < cur_best:
                cur_best = val

        score = -cur_best
        if best_val is None or score > best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]