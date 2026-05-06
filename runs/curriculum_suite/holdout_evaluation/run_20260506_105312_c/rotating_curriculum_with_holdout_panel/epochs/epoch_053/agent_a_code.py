def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (manh(nx, ny, tx, ty), nx, ny)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Choose "attack" target: best for us but worst for opponent among their nearest-ish candidates
    best_attack = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        ds = manh(sx, sy, rx, ry)
        do = manh(ox, oy, rx, ry)
        # Prefer small ds and large do; also slightly prefer closer to center
        cx, cy = w // 2, h // 2
        center_bias = manh(rx, ry, cx, cy)
        key = (ds, center_bias, -do)
        if best_attack is None or key < best_attack[0]:
            best_attack = (key, rx, ry)

    ax, ay = best_attack[1], best_attack[2]

    # Also compute opponent's closest resource to "deny"
    opp_target = None
    best_od = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        d = manh(ox, oy, rx, ry)
        if best_od is None or d < best_od:
            best_od = d
            opp_target = (rx, ry)
    bx, by = opp_target[0], opp_target[1]

    # Move scoring: go to our attack while increasing distance to opponent's target
    # (materially different from just nearest-resource pursuit).
    cx, cy = w // 2, h // 2
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = manh(nx, ny, ax, ay)
        d_opp = manh(nx, ny, bx, by)
        d_opp_from_move = manh(nx, ny, ox, oy)
        ds_now = manh(sx, sy, ax, ay)
        do_now = manh(ox, oy, bx, by)
        # Prefer progress to attack; then deny by keeping far from opponent target.
        # Use lexicographic with strong deny weight; keep deterministic tie-breakers.
        key = (d_self, d_opp, -d_opp_from_move, manh(nx, ny, cx, cy), nx, ny, ds_now, do_now)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]