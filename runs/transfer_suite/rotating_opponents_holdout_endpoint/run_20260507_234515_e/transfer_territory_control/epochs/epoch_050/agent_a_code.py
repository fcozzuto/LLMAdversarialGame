def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    obs_list = observation.get("obstacles") or []
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def norm2(x, y):
        return x * x + y * y

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unclaimed.append((int(p[0]), int(p[1])))

    opp_terr = []
    for p in (observation.get("opponent_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.append((int(p[0]), int(p[1])))

    own_terr = []
    for p in (observation.get("self_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            own_terr.append((int(p[0]), int(p[1])))

    targets = unclaimed if unclaimed else (opp_terr if opp_terr else own_terr)
    if not targets:
        if in_bounds(sx + 1, sy + 1):
            return [1, 1]
        if in_bounds(sx + 1, sy):
            return [1, 0]
        return [0, 0]

    # Deterministic tie-break: fixed move order in dirs; additional stable ordering of targets.
    targets_sorted = sorted(targets, key=lambda t: (abs(t[0] - cx) + abs(t[1] - cy), t[0], t[1]))
    t_take = targets_sorted[:min(len(targets_sorted), 18)]

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        # Prefer moves that get closer to strong targets relative to opponent, and toward center.
        center_bias = 0.15 * (-norm2(nx - cx, ny - cy))
        move_val = center_bias
        for tx, ty in t_take:
            d_me = norm2(nx - tx, ny - ty)
            d_op = norm2(ox - tx, oy - ty)
            # If we can reach closer than opponent, advantage increases.
            move_val += (d_op - d_me) * 0.003
            # Small incentive to press unclaimed, slight incentive to invade opponent territory.
            if (tx, ty) in opp_terr:
                move_val += 0.02
        # Prefer not moving too much when values close, but deterministic.
        move_val -= (abs(dx) + abs(dy)) * 0.002
        if move_val > best_val:
            best_val = move_val
            best_move = [dx, dy]

    return best_move if best_move in ([d[0], d[1]] for d in dirs) else [0, 0]