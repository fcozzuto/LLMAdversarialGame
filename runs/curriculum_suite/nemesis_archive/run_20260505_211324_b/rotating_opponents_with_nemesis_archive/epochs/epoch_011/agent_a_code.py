def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            obs.add((p[0], p[1]))
        except Exception:
            pass
    resources = []
    for r in observation.get("resources") or []:
        try:
            rx, ry = r
            resources.append((rx, ry))
        except Exception:
            pass

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    # Baselines: opponent's closest resource right now
    opp_closest = min(manh(ox, oy, rx, ry) for rx, ry in resources)

    best = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        our_closest = min(manh(nx, ny, rx, ry) for rx, ry in resources)
        lead = opp_closest - our_closest  # positive means we are closer than they are now

        # Collision/capture pressure: penalize resources where opponent can beat us
        # (approx: opponent distance now vs our distance after move)
        pressure = 0
        for rx, ry in resources:
            our_d = manh(nx, ny, rx, ry)
            opp_d = manh(ox, oy, rx, ry)
            if opp_d <= our_d:
                pressure += (our_d - opp_d + 1)

        # Small tie-break: prefer moves that also reduce opponent's closest distance to resources
        # (approx using our next position only; deterministic heuristic)
        opp_penalty = 0
        for rx, ry in resources:
            d = manh(ox, oy, rx, ry)
            if d == opp_closest:
                opp_penalty = 1

        val = (lead, -our_closest, -pressure, -opp_penalty, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best = [dx, dy]

    return best