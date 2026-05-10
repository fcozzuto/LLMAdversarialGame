def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb_dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    valid_resources = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if inb(rx, ry) and (rx, ry) not in obs:
            valid_resources.append((rx, ry))
    if not valid_resources:
        return [0, 0]

    turns = int(observation.get("turns_remaining", 0))
    best = None
    best_key = None
    for rx, ry in valid_resources:
        ds = cheb_dist(sx, sy, rx, ry)
        do = cheb_dist(ox, oy, rx, ry)
        # Primary: maximize advantage (opponent farther than us). Secondary: get closer sooner.
        adv = do - ds
        time_pref = 0
        if turns > 0:
            time_pref = 2 if ds <= turns else 0
        # Slightly discourage very far targets.
        key = (adv, time_pref, -ds, -do)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            ds = cheb_dist(nx, ny, tx, ty)
            do = cheb_dist(ox, oy, tx, ty)
            adv = do - ds
            time_pref = 0
            if turns > 0:
                time_pref = 2 if ds <= turns else 0
            # Prefer moves that improve advantage; if equal, reduce ds.
            key = (adv, time_pref, -ds, -do, -abs(nx - tx) - abs(ny - ty))
            candidates.append((key, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0], reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])]