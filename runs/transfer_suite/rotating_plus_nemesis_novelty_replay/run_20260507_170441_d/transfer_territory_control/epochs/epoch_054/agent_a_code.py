def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            blocked.add((x, y))

    # Optional helpful sets (may be absent)
    self_t = set((int(a), int(b)) for a, b in (observation.get("self_territory") or []))
    opp_t = set((int(a), int(b)) for a, b in (observation.get("opponent_territory") or []))
    unclaimed = set((int(a), int(b)) for a, b in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18
    best_dist = 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        mdx, mdy = nx - ox, ny - oy
        dist = mdx * mdx + mdy * mdy

        # Heuristic: reduce distance, prefer capturing opponent territory, avoid our own
        score = -dist
        if (nx, ny) in opp_t:
            score += 10**6
        if (nx, ny) in self_t:
            score -= 10**5
        if (nx, ny) in unclaimed:
            score += 5000

        # Deterministic tie-break: smallest dx, then dy (via lex order)
        if score > best_score or (score == best_score and (dist < best_dist or (dist == best_dist and (dx, dy) < tuple(best_move)))):
            best_score = score
            best_dist = dist
            best_move = [dx, dy]

    return best_move