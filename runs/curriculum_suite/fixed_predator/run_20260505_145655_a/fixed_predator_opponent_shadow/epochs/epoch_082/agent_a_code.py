def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def sgn(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        nx, ny = x + sgn(ox - x), y + sgn(oy - y)
        if ok(nx, ny):
            return [nx - x, ny - y]
        return [sgn(ox - x), 0] if ok(x + sgn(ox - x), y) else [0, sgn(oy - y)]

    best_tx = best_ty = None
    best_adv = None
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
        elif isinstance(r, dict):
            tx, ty = int(r.get("x")), int(r.get("y"))
        else:
            continue
        dme = man(x, y, tx, ty)
        dop = man(ox, oy, tx, ty)
        adv = (dop - dme) * 1000 - dme
        if best_adv is None or adv > best_adv or (adv == best_adv and (tx, ty) < (best_tx, best_ty)):
            best_adv = adv
            best_tx, best_ty = tx, ty

    tx, ty = best_tx, best_ty
    best_move = [0, 0]
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if not ok(nx, ny):
                continue
            dme = man(nx, ny, tx, ty)
            dop = man(ox, oy, tx, ty)
            score = (dop - dme) * 1000 - dme
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
                best_score = score
                best_move = [dx, dy]

    return best_move