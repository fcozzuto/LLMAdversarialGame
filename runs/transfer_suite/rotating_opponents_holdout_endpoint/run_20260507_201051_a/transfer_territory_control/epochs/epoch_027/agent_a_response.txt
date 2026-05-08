def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))
    st = set(map(tuple, observation.get("self_territory") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Find candidate frontier cells: unclaimed adjacent to opponent territory.
    frontier = []
    for (x, y) in unclaimed:
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            if (x + dx, y + dy) in ot:
                frontier.append((x, y))
                break
    if frontier:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        tx, ty = min(frontier, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - cx) + abs(p[1] - cy)))
        target_dx, target_dy = tx - sx, ty - sy
    else:
        # Fallback: bias toward unclaimed cells and general center.
        candidates = list(unclaimed) if unclaimed else (list(ot) if ot else [])
        if candidates:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            tx, ty = min(candidates, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy), abs(p[0] - cx) + abs(p[1] - cy)))
            target_dx, target_dy = tx - sx, ty - sy
        else:
            target_dx, target_dy = 0, 0

    opp_pos = observation.get("opponent_position", [w - 1, h - 1])[:2]
    ox, oy = opp_pos
    best = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        in_unk = (nx, ny) in unclaimed
        in_ot = (nx, ny) in ot
        in_st = (nx, ny) in st

        # Immediate capture heuristic
        val = 0
        if in_unk:
            val += 3
        if in_ot:
            val += 5  # flipping on entry
        if in_st:
            val += 1

        # Bias toward chosen direction
        align = 0
        if target_dx != 0:
            align += 1 if (dx * target_dx) > 0 else (-1 if (dx * target_dx) < 0 else 0)
        if target_dy != 0:
            align += 1 if (dy * target_dy) > 0 else (-1 if (dy * target_dy) < 0 else 0)
        val += align

        # Slightly prefer moving away from opponent to avoid counterclaim pressure
        dist_now = (sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)
        dist_next = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        val += 0.1 * (dist_next - dist_now)

        # Small tie-break: deterministic order already, but keep reproducible
        if val > best_val:
            best_val = val
            best = [dx, dy]

    return best