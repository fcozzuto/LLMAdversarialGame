def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obst

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    def best_step(ax, ay, tx, ty):
        # Greedy toward target using tie-break: prefer smaller (dx^2+dy^2), then lexicographic move
        best = None
        for mdx, mdy in moves:
            nx, ny = ax + mdx, ay + mdy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            pen = mdx * mdx + mdy * mdy
            key = (d, pen, mdx, mdy, nx, ny)
            if best is None or key < best[0]:
                best = (key, (mdx, mdy))
        return best[1] if best else (0, 0)

    if not resources:
        return [0, 0]

    # Predict opponent target as nearest resource to them; then predict their greedy next step.
    # Use a minimal heuristic to reduce thrashing: if multiple resources equally close, pick the one
    # with smallest manhattan sum (tie-break deterministically).
    def pick_nearest(ax, ay):
        best = None
        for rx, ry in resources:
            d = man(ax, ay, rx, ry)
            tie = d
            key = (d, tie, rx, ry)
            if best is None or key < best:
                best = key
                tx, ty = rx, ry
        return tx, ty

    op_tx, op_ty = pick_nearest(ox, oy)
    op_step = best_step(ox, oy, op_tx, op_ty)
    n_ox, n_oy = ox + op_step[0], oy + op_step[1]

    # Evaluate our candidate moves by anticipating capture race on our next position.
    best_move = (None, None)
    best_score = None
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not legal(nx, ny):
            continue

        # If we move onto a resource, prioritize heavily.
        gain = 0
        for rx, ry in resources:
            if rx == nx and ry == ny:
                gain = 1000000
                break

        # Choose our best target from the new position (greedy, deterministic).
        my_tx, my_ty = pick_nearest(nx, ny)

        # Approximate opponent threat after their predicted move:
        # Compare our distance to our target vs opponent distance to same target.
        self_d = man(nx, ny, my_tx, my_ty)
        opp_d = man(n_ox, n_oy, my_tx, my_ty)

        # Also penalize moving toward a target that opponent can reach sooner.
        # Small bias to keep progress: prefer smaller self_d.
        race = (opp_d - self_d)  # larger is better
        progress = -self_d

        score = gain + 50 * race + 2 * progress

        key = (-(gain > 0), -race, self_d, mdx, mdy)
        if best_score is None or (score > best_score) or (score == best_score and key < best_move[0]):
            best_score = score
            best_move = (key, [mdx, mdy])

    return best_move[1] if best_move[1] else [0, 0]