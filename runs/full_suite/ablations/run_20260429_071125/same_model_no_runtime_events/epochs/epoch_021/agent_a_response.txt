def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            if "pos" in r and isinstance(r.get("pos"), (list, tuple)) and len(r["pos"]) >= 2:
                resources.append((int(r["pos"][0]), int(r["pos"][1])))
            else:
                x = r.get("x", None)
                y = r.get("y", None)
                if x is not None and y is not None:
                    resources.append((int(x), int(y)))

    if not resources or not valid(sx, sy):
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = None
    best_score = None
    for rx, ry in resources:
        md = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        advantage = od - md  # positive if we are closer
        # prioritize immediate gain while avoiding race-losing targets
        score = (-advantage, md, rx, ry)
        if best is None or score < best_score:
            best = (rx, ry)
            best_score = score

    tx, ty = best
    # choose move that improves step toward target and keeps us safe, while discouraging positions closer to opponent target
    cx = 0
    if tx > sx: cx = 1
    elif tx < sx: cx = -1
    cy = 0
    if ty > sy: cy = 1
    elif ty < sy: cy = -1
    preferred = (cx, cy)

    options = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            nd_to_t = cheb(nx, ny, tx, ty)
            nd_opp_t = cheb(nx, ny, tx, ty)  # same target; use opponent proximity as tie-break via their distance
            op_to_t = cheb(ox, oy, tx, ty)
            # lower is better; keep preferred direction strong
            dir_bonus = 0 if (dx, dy) == preferred else 1
            # if we are still losing the race (op closer), we prefer routes that increase advantage (reduce our distance)
            score = (dir_bonus, nd_to_t, - (op_to_t - nd_to_t), nd_opp_t, nx, ny)
            options.append((score, [dx, dy]))

    if not options:
        return [0, 0]
    options.sort(key=lambda x: x[0])
    return options[0][1]