def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    # Pick a target that maximizes how much closer we are than the opponent, with deterministic tie breaks.
    best = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds  # positive => we are closer
        # Prefer resources we can reach sooner; bias toward center for ties.
        center_bias = man(rx, ry, (w - 1) // 2, (h - 1) // 2)
        key = (-adv, ds, center_bias, rx, ry)  # smaller is better after negating adv
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Opponent's likely next step toward our chosen target.
    opp_next = (ox, oy)
    best_od = None
    for dx, dy in deltas:
        nx, ny = ox + dx, oy + dy
        if not inb(nx, ny):
            continue
        od = man(nx, ny, tx, ty)
        if best_od is None or od < best_od or (od == best_od and (nx, ny) < opp_next):
            best_od = od
            opp_next = (nx, ny)

    # Score each of our candidate moves.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d_t = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)

        # Encourage moving toward target; discourage letting opponent get too good at it.
        cur_ds = man(sx, sy, tx, ty)
        cur_do = man(ox, oy, tx, ty)
        # Expected contest pressure: who can reduce distance faster.
        opp_ds_after = min(
            man(ox + pdx, oy + pdy, tx, ty)
            for pdx, pdy in deltas
            if inb(ox + pdx, oy + pdy)
        )
        progress = cur_ds - d_t
        opp_pressure = cur_do - opp_ds_after  # opponent improvement toward target

        # Block if we step onto opponent's next cell, otherwise if adjacent to it.
        block = 0
        if (nx, ny) == opp_next:
            block = 20
        else:
            block = 4 if max(abs(nx - opp_next[0]), abs(ny - opp_next[1])) == 1 else 0

        # Also add mild reward for keeping distance from opponent (prevents bad swaps).
        center = man(nx, ny, (w - 1) // 2, (h - 1) // 2)
        score = (progress * 10 + block + d_opp * 0.5 - d_t * 2.2 - opp_pressure * 4.0 - center * 0.05)

        if best_score is None or score > best_score or (score == best_score and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_score = score
            best_move = (dx, dy)