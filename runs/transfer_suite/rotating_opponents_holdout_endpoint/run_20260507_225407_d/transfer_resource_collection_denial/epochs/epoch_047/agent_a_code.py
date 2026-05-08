def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]

    # If on a resource, stay.
    for x, y in res:
        if x == sx and y == sy:
            return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def best_from(px, py):
        best_adv = -10**9
        best_sd = 10**9
        best_td = 10**9
        for tx, ty in res:
            sd = man(px, py, tx, ty)
            td = man(ox, oy, tx, ty)
            adv = td - sd  # positive: we arrive earlier
            if adv > best_adv or (adv == best_adv and (sd < best_sd or (sd == best_sd and td < best_td))):
                best_adv, best_sd, best_td = adv, sd, td
        return best_adv, best_sd, best_td

    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            valid_moves.append((dx, dy))

    if not valid_moves:
        return [0, 0]

    # Prefer moves that keep our advantage high; deterministic tie-break by fixed move order.
    chosen = None
    chosen_key = None
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        adv, sd, td = best_from(nx, ny)
        key = (adv, -sd, -td, dx, dy)  # earlier pickup + avoid letting opponent benefit
        if chosen_key is None or key > chosen_key:
            chosen_key = key
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]