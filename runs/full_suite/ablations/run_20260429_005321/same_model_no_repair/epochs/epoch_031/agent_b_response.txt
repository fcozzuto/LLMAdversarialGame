def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    obs_set = {(x, y) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    # Strategic switch to force materially different behavior this epoch
    # even turns: grab nearest; odd turns: hunt resources where we're closer than opponent.
    nearest = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))
    if observation.get("turn_index", 0) % 2 == 0:
        tx, ty = nearest
    else:
        best = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # strongly prefer opportunities where we have distance advantage
            val = (do - ds) * 1000 + (do - ds) * 10 - ds - (rx * 7 + ry)
            if best is None or val > best[0]:
                best = (val, rx, ry)
        tx, ty = best[1], best[2]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**30

    # obstacle proximity penalty
    obs_list = obstacles

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue

        val = 0

        # If we can collect immediately
        if (nx, ny) in {(r[0], r[1]) for r in resources}:
            val += 10**7

        # Approach target
        d_new = man(nx, ny, tx, ty)
        d_now = man(sx, sy, tx, ty)
        val += (d_now - d_new) * 500 - d_new

        # Also consider how much we reduce opponent's ability to reach the same target
        do_now = man(ox, oy, tx, ty)
        do_after = do_now  # opponent doesn't move here; still compare our position vs theirs
        ds_after = d_new
        val += (do_after - ds_after) * 200

        # Avoid getting cornered: keep away from obstacles and opponent
        for ex, ey in obs_list:
            d = max(abs(nx - ex), abs(ny - ey))
            if d == 0:
                val -= 10**9
            elif d == 1:
                val -= 250
            elif d == 2:
                val -= 60
            elif d == 3:
                val -= 15

        oppd = max(abs(nx - ox), abs(ny - oy))
        val -= max(0, 3 - oppd) * 120

        # Tie-break deterministically toward