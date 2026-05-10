def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    opp_t = observation.get("opponent_territory") or []
    self_t = observation.get("self_territory") or []
    unclaimed = observation.get("unclaimed_cells") or []

    self_set = {(int(p[0]), int(p[1])) for p in self_t if isinstance(p, (list, tuple)) and len(p) >= 2}
    opp_set = {(int(p[0]), int(p[1])) for p in opp_t if isinstance(p, (list, tuple)) and len(p) >= 2}
    un_set = {(int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}

    px = int(sx)
    py = int(sy)
    opp_pos = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Precompute a couple of reference targets deterministically
    # 1) if any opponent territory exists, use nearest
    # 2) else use nearest unclaimed
    targets = None
    if opp_set:
        targets = list(opp_set)
    elif un_set:
        targets = list(un_set)

    # If still none, drift to center-ish
    if not targets:
        targets = [(w // 2, h // 2)]

    # Pick deterministic nearest target to guide movement
    best_t = targets[0]
    best_td = abs(targets[0][0] - px) + abs(targets[0][1] - py)
    for tx, ty in targets[1:]:
        d = abs(tx - px) + abs(ty - py)
        if d < best_td or (d == best_td and (tx, ty) < best_t):
            best_td = d
            best_t = (tx, ty)

    tx, ty = best_t
    tx2, ty2 = ox, oy  # also bias towards opponent position

    for dx, dy in deltas:
        nx, ny = px + dx, py + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        if (nx, ny) in opp_set:
            # Enter opponent territory: strong flip incentive
            score = 1000 - (abs(nx - tx) + abs(ny - ty))
        elif (nx, ny) in un_set:
            # Claiming unclaimed cells
            score = 300 - (abs(nx - tx) + abs(ny - ty))
        elif (nx, ny) in self_set:
            # Stay inside own territory: low, but still allow progress
            score = 50 - (abs(nx - tx) + abs(ny - ty))
        else:
            # Unknown/other: minimal incentive
            score = 10 - (abs(nx - tx) + abs(ny - ty))

        # Additional steering towards opponent position and target
        score -= 0.1 * (abs(nx - tx2) + abs(ny - ty2))

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]