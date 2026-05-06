def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) == 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # Center-ish / stay safe: move to maximize distance from opponent.
        best = None
        for dx, dy, nx, ny in legal:
            key = (-man(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Opponent greedy target
    best_tr = resources[0]
    best_d = man(ox, oy, best_tr[0], best_tr[1])
    for r in resources[1:]:
        d = man(ox, oy, r[0], r[1])
        if d < best_d:
            best_d = d
            best_tr = r
    tx, ty = best_tr[0], best_tr[1]

    # Predict opponent "next" step toward target (deny near that cell)
    ddx = tx - ox
    sdx = 1 if ddx > 0 else (-1 if ddx < 0 else 0)
    ddy = ty - oy
    sdy = 1 if ddy > 0 else (-1 if ddy < 0 else 0)

    # Enumerate predicted next options (greedy step + alternatives)
    pref_next = []
    for ax in (-1, 0, 1):
        for ay in (-1, 0, 1):
            nx, ny = ox + sdx + ax, oy + sdy + ay
            if inside(nx, ny):
                # Prefer moves closer to target
                pref_next.append((man(nx, ny, tx, ty), nx, ny))
    if pref_next:
        pref_next.sort()
        denx, deny = pref_next[0][1], pref_next[0][2]
    else:
        denx, deny = ox + sdx, oy + sdy

    # Race + denial score: reach target sooner, and/or occupy predicted next cell neighborhood
    best = None
    for dx, dy, nx, ny in legal:
        our_to_t = man(nx, ny, tx, ty)
        opp_to_t = man(denx, deny, tx, ty)
        our_race = our_to_t - opp_to_t  # negative is good: we are closer than opponent near their next
        # Denial: if we can get close to predicted next, block
        deny_dist = man(nx, ny, denx, deny)
        # Also slightly prefer moving toward target when denial is not possible
        tgt_dist = our_to_t

        # Strongly discourage moving away from target when resources exist
        key = (our_race, deny_dist, tgt_dist, abs(nx - sx) + abs(ny - sy), dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]