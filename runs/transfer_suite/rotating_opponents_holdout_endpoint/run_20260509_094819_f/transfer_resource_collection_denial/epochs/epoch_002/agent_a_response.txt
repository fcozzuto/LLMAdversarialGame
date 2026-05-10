def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def best_step(tx, ty):
        best = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man(nx, ny, tx, ty)
            # Try to avoid marching into opponent while still aiming for target
            do = man(nx, ny, ox, oy)
            # Also consider next-step "safety" by preferring cells that keep distance larger
            key = (d, -do, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    if not resources:
        # Drift to a corner that is far from opponent (shadow opponents often contest/harass)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda p: (man(p[0], p[1], ox, oy), -p[0], -p[1]))
        return best_step(tx, ty)

    # Choose a resource where we are ahead most decisively; if none, choose least-losing option.
    chosen = None
    chosen_key = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # primary: maximize (od - sd) => bigger means we're closer/even
        # secondary: minimize our distance to secure it quickly
        # tertiary: deterministic tie by coordinates
        key = (-(od - sd), sd, rx, ry)
        if chosen_key is None or key < chosen_key:
            chosen_key = key
            chosen = (rx, ry)

    tx, ty = chosen
    # If we're not ahead for the chosen resource, try to "shadow" by moving to a cell
    # that increases our chance: prefer steps that reduce our distance and also reduce opponent approach.
    step = best_step(tx, ty)

    # One-step tactical tweak: if the step does not reduce our distance (blocked/diagonal tie),
    # move toward position that maximizes opponent-distance while not increasing our distance.
    cur_d = man(sx, sy, tx, ty)
    nsx, nsy = sx + step[0], sy + step[1]
    if man(nsx, nsy, tx, ty) > cur_d:
        best2 = None
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            nd = man(nx, ny, tx, ty)
            if nd > cur_d:
                continue
            do = man(nx, ny, ox, oy)
            key2 = (-do, nd, dx, dy, nx, ny)
            if best2 is None or key2 < best2[0]:
                best2 = (key2, [dx, dy])
        if best2 is not None:
            return best2[1]
    return step