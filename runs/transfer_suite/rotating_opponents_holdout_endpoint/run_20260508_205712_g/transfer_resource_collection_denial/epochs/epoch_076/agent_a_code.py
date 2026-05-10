def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dself = dist(nx, ny, ox, oy)
            key = (-dself, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    # Choose move that maximizes "we beat opponent to a resource" advantage.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Penalize getting too close to opponent unless we can capture first.
        opp_close = dist(nx, ny, ox, oy)

        best_adv = None
        best_res_tie = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) == (nx, ny):
                adv = 10**6  # immediate collection
            else:
                ds = dist(nx, ny, rx, ry)
                do = dist(ox, oy, rx, ry)
                # If ds < do, we are earlier (good). If ds > do, bad.
                adv = (do - ds)  # higher is better

            # Small deterministic tie-break: prefer resources with smaller coordinates
            tie = (-(rx + ry), rx, ry)
            if best_adv is None or adv > best_adv or (adv == best_adv and tie < best_res_tie):
                best_adv = adv
                best_res_tie = tie

        # Overall key: primary best_adv, then avoid opponent, then prefer x-progress toward opponent side
        tx = 1 if ox > nx else -1 if ox < nx else 0
        xprog = tx * (dx)
        key = (-best_adv, opp_close, -xprog, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]