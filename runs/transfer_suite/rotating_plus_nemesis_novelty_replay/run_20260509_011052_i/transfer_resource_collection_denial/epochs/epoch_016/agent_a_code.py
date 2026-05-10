def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    # Evaluate one-step move by advantage over opponent to the best available resource.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        best_adv = -10**9
        best_steal = -10**9
        best_selfd = 10**9
        for rx, ry in res:
            self_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            # Prefer resources where we are already closer (steal likelihood),
            # otherwise still choose the one we can "catch up" to most quickly.
            adv = opp_d - self_d
            if self_d < best_selfd and adv >= 0:
                pass
            if adv > best_adv:
                best_adv = adv
            # Stronger bias towards being closer than opponent.
            steal = adv * 100 - self_d
            if steal > best_steal:
                best_steal = steal
                best_selfd = self_d

        # Deterministic tie-break: higher steal, then higher adv, then smaller distance, then lexicographic dx,dy.
        cand = (best_steal, best_adv, -best_selfd, dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [int(best[3]), int(best[4])]