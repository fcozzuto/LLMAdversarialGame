def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set((x, y) for x, y in obstacles)
    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh
    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0: d1 = -d1
        d2 = ay - by
        if d2 < 0: d2 = -d2
        return d1 + d2

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    # Pick best target resource where we are relatively closer; deterministic tie-breaks.
    best_t = None
    best_score = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        lead = do - ds  # positive means we are closer
        # Small bias to push toward center-ish to reduce pathing stalls
        center_bias = -0.01 * ((rx - (gw - 1) / 2) ** 2 + (ry - (gh - 1) / 2) ** 2)
        # Prefer non-stuck targets
        score = lead * 1000 - ds * 2 + center_bias
        key = (-(lead), ds, rx, ry)  # for determinism when score close
        if best_score is None or (score > best_score) or (score == best_score and key < best_t[0]):
            best_score = score
            best_t = (key, (rx, ry))

    if best_t is None:
        tx, ty = resources[0]
    else:
        tx, ty = best_t[1]

    # If the opponent is already much closer to all resources, still move to the least-bad one.
    if best_score is not None and best_score < -200:
        tx, ty = sorted(resources, key=lambda p: (man(sx, sy, p[0], p[1]) - man(ox, oy, p[0], p[1]), p[0], p[1]))[0]

    # Choose move that improves our distance to target while not walking into obstacles.
    best_move = (0, 0)
    best_eval = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds2 = man(nx, ny, tx, ty)
        do2 = man(ox, oy, tx, ty)
        # Encourage taking leads and avoid moves that let opponent get too close in next step.
        # Estimate opponent next step distance to our next position.
        mind_op = 10**9
        for odx, ody in deltas:
            px, py = ox + odx, oy + ody
            if inb(px, py) and (px, py) not in obs:
                d = man(px, py, nx, ny)
                if d < mind_op:
                    mind_op = d
        opp_pressure = -50 if mind_op <= 1 else -10 if mind_op <= 2 else 0

        lead_now = do2 - ds2
        evalv = lead_now * 1000 - ds2 * 2 + opp_pressure + (-(dx * dx + dy * dy)) * 1e-6
        key = (-evalv, dx, dy)
        if best_eval is None or evalv > best_eval or (evalv == best_eval and key < (None if best_eval is None else best_eval)):
            best_eval = evalv
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]