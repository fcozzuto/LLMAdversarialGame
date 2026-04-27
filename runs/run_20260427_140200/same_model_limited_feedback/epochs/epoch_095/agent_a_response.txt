def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        # No resources: move away from opponent while avoiding obstacles
        deltas = [[dx, dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        deltas.remove([0, 0])
        best, bestd = [0, 0], -1
        for dx, dy in deltas + [[0, 0]]:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
                continue
            d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            if d > bestd:
                bestd, best = d, [dx, dy]
        return best

    def dist2(a, b):
        return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])

    us = (sx, sy)
    opp = (ox, oy)

    # Pick a resource we are not too far behind (prefer winning opportunities), otherwise nearest.
    best_r, best_key = None, None
    for r in resources:
        r = tuple(r)
        if r in obstacles:
            continue
        d_u = dist2(us, r)
        d_o = dist2(opp, r)
        # Key: prefer resources where we are closer than opponent; then minimize our distance; then tie-break deterministically.
        key = (0 if d_u <= d_o else 1, d_u, (r[0], r[1]))
        if best_key is None or key < best_key:
            best_key, best_r = key, r

    tx, ty = best_r
    deltas = [[dx, dy] for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Always allow staying; keep deterministic order.
    scored = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        # Primary: reduce distance to target; Secondary: discourage moving toward opponent when not winning.
        d_t = dist2((nx, ny), (tx, ty))
        d_o = dist2((nx, ny), opp)
        # If opponent is closer to target, add slight penalty for reducing their advantage.
        opp_adv_pen = 0
        if dist2(opp, (tx, ty)) < dist2(us, (tx, ty)):
            opp_adv_pen = -d_o * 0.001
        key = (d_t, opp_adv_pen, (nx, ny))
        scored.append((key, [dx, dy]))
    if scored:
        scored.sort(key=lambda x: x[0])
        return scored[0][1]

    # Fallback: no legal step toward target (all blocked) -> move to safest legal cell.
    best, best_key = [0, 0], None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        key = (-(dist2((nx, ny), opp)), (nx, ny))
        if best_key is None or key < best_key:
            best_key, best = key, [dx, dy]
    return best