def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or (0, 0)
    o = observation.get("opponent_position") or (0, 0)
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])
    sx = 0 if sx < 0 else (w - 1 if sx >= w else sx)
    sy = 0 if sy < 0 else (h - 1 if sy >= h else sy)
    ox = 0 if ox < 0 else (w - 1 if ox >= w else ox)
    oy = 0 if oy < 0 else (h - 1 if oy >= h else oy)

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

    res_set = set(resources)

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # immediate capture bonus
        immediate = 1 if (nx, ny) in res_set else 0

        best_adv = -10**9
        best_self_steps = 10**9
        best_opp_steps = 10**9
        best_tx = 0
        best_ty = 0
        for tx, ty in resources:
            ds = dist(nx, ny, tx, ty)
            do = dist(ox, oy, tx, ty)
            adv = do - ds
            if adv > best_adv or (adv == best_adv and (ds < best_self_steps or (ds == best_self_steps and (do < best_opp_steps or (do == best_opp_steps and (tx, ty) > (best_tx, best_ty)))))):
                best_adv = adv
                best_self_steps = ds
                best_opp_steps = do
                best_tx, best_ty = tx, ty

        # Prefer moves that secure advantage quickly; if tie, reduce self distance.
        score = (immediate, best_adv, -best_self_steps, -best_opp_steps, best_tx, best_ty)
        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move