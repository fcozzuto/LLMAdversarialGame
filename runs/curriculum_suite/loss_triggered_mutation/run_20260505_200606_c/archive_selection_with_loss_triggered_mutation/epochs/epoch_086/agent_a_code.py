def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Pick target resource that we can reach earlier than opponent; deterministic tie-break by coords.
    def best_target_from(x, y):
        best = None  # (adv, self_d, ox_d, rx, ry)
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = man(x, y, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = sd - od  # smaller is better (we "beat" opponent)
            key = (adv, sd, od, rx, ry)
            if best is None or key < best:
                best = key
        return best[-2], best[-1]

    tx, ty = best_target_from(sx, sy)

    # Greedy step: minimize (self progress to target vs opponent progress),
    # with safety penalty near opponent and small bias toward improving position.
    best_move = None  # (score, nx, ny, dx, dy)
    cur_to_tx = man(sx, sy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        self_d = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        # Aim to reduce opponent advantage and continue approaching target.
        score = (self_d - opp_d) * 100 + self_d
        # Safety: avoid stepping adjacent to opponent when not improving target.
        d_opp = man(nx, ny, ox, oy)
        if d_opp <= 1 and self_d >= cur_to_tx:
            score += 50
        # If target is unreachable by immediate move, still keep moving closer.
        # Small deterministic tie-break by coords.
        score += nx * 0 + ny * 0
        key = (score, nx, ny, dx, dy)
        if best_move is None or key < best_move:
            best_move = key

    if best_move is None:
        return [0, 0]
    return [int(best_move[-2]), int(best_move[-1])]