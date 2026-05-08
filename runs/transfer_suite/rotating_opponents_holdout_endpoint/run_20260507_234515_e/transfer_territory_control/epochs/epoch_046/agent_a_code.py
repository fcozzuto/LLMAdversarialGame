def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]) if len(sp) > 0 else 0, int(sp[1]) if len(sp) > 1 else 0
    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]) if len(op) > 0 else w - 1, int(op[1]) if len(op) > 1 else h - 1

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    self_set = set((int(p[0]), int(p[1])) for p in self_t if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_t if isinstance(p, (list, tuple)) and len(p) >= 2)

    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2)
    resources = observation.get("resources") or []
    res_set = set((int(p[0]), int(p[1])) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx, dy = a - c, b - d
        return abs(dx) + abs(dy)

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        base = 0
        if (nx, ny) in opp_set:
            base += 6
        if (nx, ny) in un_set:
            base += 3
        if (nx, ny) in res_set:
            base += 2
        if (nx, ny) in self_set:
            base += 1

        d_center = abs(nx - cx) + abs(ny - cy)
        d_enemy = abs(nx - ox) + abs(ny - oy)
        # Prefer moves toward center and toward unclaimed; also prefer staying away from enemy to avoid being sandwiched.
        nearest_un = 0
        if unclaimed:
            # cheap estimate: sample up to 8 unclaimed cells deterministically
            bestdu = 10**9
            step = max(1, len(unclaimed) // 8)
            for i in range(0, len(unclaimed), step):
                p = unclaimed[i]
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    px, py = int(p[0]), int(p[1])
                    du = abs(px - nx) + abs(py - ny)
                    if du < bestdu:
                        bestdu = du
            nearest_un = bestdu if bestdu < 10**9 else 0

        score = base + (-0.15 * d_center) + (0.10 * d_enemy) + (-0.25 * nearest_un)
        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    # Deterministic tie-break: higher score, then dx, then dy
    candidates.sort(key=lambda t: (t[0], t[1], t[2]), reverse=True)
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]