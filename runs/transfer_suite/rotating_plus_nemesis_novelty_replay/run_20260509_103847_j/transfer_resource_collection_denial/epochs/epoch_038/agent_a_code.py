def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick resource with best self-vs-opp advantage (self closer / opp farther), break ties by nearer to self.
    best_r = None
    best_adv_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Advantage: higher is better; encode as sort key where smaller is better
        # Prefer: larger (do - ds); then smaller ds; then lexicographic
        key = (- (do - ds), ds, rx, ry)
        if best_adv_key is None or key < best_adv_key:
            best_adv_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    cur_ds = man(sx, sy, tx, ty)

    # Move evaluation: maximize advantage improvement; avoid walking into bad areas (by distance to top contested resources).
    top2 = []
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        adv = do - ds
        top2.append((adv, ds, rx, ry))
    top2.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))
    contested = [(top2[0][2], top2[0][3], top2[0][0])]
    if len(top2) > 1:
        contested.append((top2[1][2], top2[1][3], top2[1][0]))

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_new = man(nx, ny, tx, ty)
        do_to_target = man(ox, oy, tx, ty)

        # Main: reduce distance to target and keep (or increase) advantage over opponent.
        adv_before = do_to_target - cur_ds
        adv_after = do_to_target - ds_new
        score = (adv_after - adv_before) * 1000 - ds_new

        # Secondary: don't let opponent's best contest get much closer to us (soft blocking).
        block_pen = 0
        for cx, cy, _ in contested:
            block_pen += (man(nx, ny, cx, cy) - man(sx, sy, cx, cy))
        score -= block_pen

        # Tiny deterministic tie-break: prefer moves that also move closer to opponent (to prevent stealing), but only if it doesn't increase our target distance.
        if ds_new <= cur_ds:
            score += -man(nx, ny, ox, oy)

        # Deterministic tie-break by dx,dy ordering to ensure no ambiguity.
        cand = (-(score), dx, dy)
        if best_score is None or cand < best_score:
            best_score = cand
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]