def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("evade" in role) or ("runner" in role)

    if (sx, sy) == (ox, oy):
        return [0, 0]

    deltas = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    mobility_deltas = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def mobility(x, y):
        c = 0
        for dx, dy in mobility_deltas:
            nx, ny = x + dx, y + dy
            if (dx or dy) and ok(nx, ny):
                c += 1
        return c

    # Prefer safer movement always; strategy differs by sign.
    # Tie-break deterministically by (score, dx, dy).
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        mob = mobility(nx, ny)

        # Small obstacle-aware steering: avoid being adjacent to obstacles.
        adj_obs = 0
        for ax, ay in [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in blocked:
                adj_obs += 1

        if is_evader:
            # Run to increase distance; keep mobility; avoid clutter; also favor edges/corners away from pursuer.
            edge_bonus = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
            # Smaller edge_bonus = closer to edge; push toward edges by subtracting.
            score = dist2 + 0.4 * mob - 0.8 * adj_obs - 0.05 * edge_bonus
        else:
            # Pursue: decrease distance; keep mobility; avoid clutter; slightly prefer lines toward opponent.
            line = -(abs(nx - ox) + abs(ny - oy))
            score = -dist2 + 0.35 * mob - 0.8 * adj_obs + 0.02 * line

        key = (score, -dx, -dy)  # deterministic tie-break
        if best is None or key > best[0]:
            best = (key, dx, dy)

    return [int(best[1]), int(best[2])]