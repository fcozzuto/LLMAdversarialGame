def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obst)
    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_for_pos(px, py):
        best_key = None
        best_r = resources[0]
        for rx, ry in resources:
            our_d = md(px, py, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            key = (our_d, -opp_d, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        return best_r

    tx, ty = best_for_pos(sx, sy)

    best_move = (0, 0)
    best_eval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        n_tx, n_ty = best_for_pos(nx, ny)
        our_d = md(nx, ny, n_tx, n_ty)
        opp_d = md(ox, oy, n_tx, n_ty)

        # Encourage breaking ties toward resources we can reach sooner and being harder to contest.
        # Also keep some angular stability by preferring moves that reduce distance to the current target.
        cur_d = md(sx, sy, tx, ty)
        new_d = md(nx, ny, tx, ty)
        progress = new_d - cur_d  # negative is good

        # Slightly avoid moving closer to opponent unless we also improve resource access.
        adj = md(nx, ny, ox, oy)
        my_adj = md(sx, sy, ox, oy)
        opp_approach = adj - my_adj  # negative means getting closer

        eval_key = (our_d, -opp_d, abs(n_tx - nx), abs(n_ty - ny), progress, opp_approach, dx, dy)
        if best_eval is None or eval_key < best_eval:
            best_eval = eval_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]