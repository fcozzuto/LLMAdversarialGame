def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target resource we can arrive first; otherwise pick best contested tradeoff.
    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) == 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        if not valid(tx, ty):
            continue
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        # Key: prefer sd<od (positive advantage), then minimal sd, then farther from opponent in same direction.
        adv = od - sd
        key = (-adv, sd, abs(tx - sx) + abs(ty - sy), abs(tx - ox) + abs(ty - oy), tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        # Deterministic fallback: move toward center-left bias.
        tx, ty = (1 if sx > w // 2 else w - 2, h // 2)
    else:
        tx, ty = best

    # Candidate one-step moves (including staying still), ordered deterministically.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                candidates.append((dx, dy, man(nx, ny, tx, ty), man(nx, ny, ox, oy)))
    if not candidates:
        return [0, 0]

    # Choose move that reduces our distance to target most; if tie, increases distance from opponent.
    candidates.sort(key=lambda t: (t[2], -t[3], t[0], t[1]))
    return [candidates[0][0], candidates[0][1]]