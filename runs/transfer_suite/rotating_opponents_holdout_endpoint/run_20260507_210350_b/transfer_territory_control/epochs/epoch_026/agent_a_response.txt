def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = observation.get("unclaimed_cells") or []
    if not unclaimed:
        unclaimed = observation.get("self_territory") or []

    opp = observation.get("opponent_position") or [None, None]
    ox = int(opp[0]) if opp[0] is not None else None
    oy = int(opp[1]) if opp[1] is not None else None

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    center_x = (w - 1) / 2.0
    center_y = (h - 1) / 2.0

    def clamp_min_dist_to_obstacles(nx, ny):
        md = 999
        for (ox2, oy2) in obstacles:
            d = abs(nx - ox2) + abs(ny - oy2)
            if d < md:
                md = d
        return 0 if md == 999 else md

    def min_dist_to_unclaimed(nx, ny):
        md = 999
        for p in unclaimed:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    d = abs(nx - x) + abs(ny - y)
                    if d < md:
                        md = d
        return 0 if md == 999 else md

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    best = None
    best_key = None
    for dx, dy, nx, ny in valid:
        dist_center = abs(nx - center_x) + abs(ny - center_y)
        dist_opp = 0
        if ox is not None and oy is not None:
            dist_opp = abs(nx - ox) + abs(ny - oy)
        dist_obs = clamp_min_dist_to_obstacles(nx, ny)
        dist_unclaimed = min_dist_to_unclaimed(nx, ny)

        # Prefer: closer to center (deny center claim), keep away from opponent, and expand towards unclaimed.
        score = (-dist_center) + 0.06 * dist_opp + 0.03 * dist_obs + 0.02 * (-dist_unclaimed)

        # Deterministic tie-break: higher score, then lexicographic move bias
        key = (-score, dx, dy, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]