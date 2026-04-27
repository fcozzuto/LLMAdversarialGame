def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Strategic shift: pick the resource where we have the greatest distance advantage over the opponent.
    if resources:
        best_tx, best_ty = resources[0]
        best_adv = -10**9
        for tx, ty in resources:
            dm = manh(mx, my, tx, ty)
            do = manh(ox, oy, tx, ty)
            adv = do - dm  # higher => we are closer than opponent
            # tie-break deterministically: smaller dm, then smaller x,y
            if adv > best_adv or (adv == best_adv and (dm < manh(mx, my, best_tx, best_ty) or (dm == manh(mx, my, best_tx, best_ty) and (tx, ty) < (best_tx, best_ty)))):
                best_adv = adv
                best_tx, best_ty = tx, ty
    else:
        best_tx, best_ty = ox, oy

    # Move selection: minimize distance to chosen target, discourage getting closer to opponent, slight obstacle-safe bias.
    cand_best = (-10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not inb(nx, ny):
            continue
        d_target = manh(nx, ny, best_tx, best_ty)
        d_opp = manh(nx, ny, ox, oy)
        # Prefer keeping some separation unless target is urgent.
        score = (-d_target) + (0.15 * d_opp)
        # Strongly prefer immediate reaching the target.
        if (nx, ny) == (best_tx, best_ty):
            score += 1000
        # Deterministic tie-break: prefer larger separation if tied, then fixed ordering via dx,dy.
        if score > cand_best[0] or (score == cand_best[0] and (d_opp > cand_best[1] or (d_opp == cand_best[1] and (dx, dy) > (cand_best[2], cand_best[3] if False else 0)))):
            cand_best = (score, d_opp, dx, dy)

    return [int(cand_best[2]), int(cand_best[3])]