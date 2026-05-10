def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inside(nx, ny) and (nx, ny) not in obs

    opp_set = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            opp_set.add((int(p[0]), int(p[1])))

    un_list = observation.get("unclaimed_cells") or []
    if not un_list:
        un_list = observation.get("resources") or []
    targets = []
    if un_list:
        for p in un_list:
            if not (isinstance(p, (list, tuple)) and len(p) == 2):
                continue
            x, y = int(p[0]), int(p[1])
            if not inside(x, y):
                continue
            # Prefer cells adjacent to opponent territory (edge-breaking)
            adj = False
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
                if (x + dx, y + dy) in opp_set:
                    adj = True
                    break
            targets.append((x, y, 1 if adj else 0))
    if not targets:
        return [0, 0]

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def md(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    # Evaluate moves: minimize distance to best target, prefer cutting toward opponent.
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        best_d = 10**9
        best_adj = -1
        best_to_opp = 10**9
        for tx, ty, adj in targets:
            d = md(nx, ny, tx, ty)
            if d < best_d or (d == best_d and (adj > best_adj or (adj == best_adj and md(nx, ny, ox, oy) < best_to_opp))):
                best_d = d
                best_adj = adj
                best_to_opp = md(nx, ny, ox, oy)

        # Score: strongly prefer adjacent-to-opponent targets; then approach them; then improve proximity to opponent.
        sc = (-2 * best_adj) * 1000 - best_d * 3 - best_to_opp
        cand = (sc, best_adj, -best_to_opp, -abs(dx) - abs(dy), dx, dy)
        if best is None or cand > best:
            best = cand

    return [int(best[4]), int(best[5])]