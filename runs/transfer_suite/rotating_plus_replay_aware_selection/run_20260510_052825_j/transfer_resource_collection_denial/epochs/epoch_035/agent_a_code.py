def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    valid = []
    for r in resources:
        x, y = r[0], r[1]
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    tr = int(observation.get("turns_remaining", 0))
    rem = observation.get("remaining_resource_count", len(valid))
    few = (tr <= 6) or (rem <= 3)

    best_t = None
    best_v = None
    for rx, ry in valid:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        margin = od - sd  # positive if we are closer
        # small bias away from obstacles by discouraging targets adjacent to obstacles
        adj_obs = 0
        if (rx + 1, ry) in obstacles or (rx - 1, ry) in obstacles or (rx, ry + 1) in obstacles or (rx, ry - 1) in obstacles:
            adj_obs = 1

        # Keep focus on winning races; when few left, greedier to secure.
        v = margin * 2.8 - sd * (0.55 if not few else 0.95) - adj_obs * 0.35
        if sd <= 1:
            v += 3.2
        # Secondary tie-break: prefer lower self-distance and (slightly) higher y then x (stable)
        v += (-sd) * (0.02 if not few else 0.05) + (ry * 0.001 + rx * 0.0007)

        if best_v is None or v > best_v:
            best_v = v
            best_t = (rx, ry)

    tx, ty = best_t
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If immediate diagonal would land on an obstacle, fall back to a safe axis move.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # try axis-aligned safe moves deterministically
        cand = []
        if (sx + dx, sy) not in obstacles:
            cand.append((dx, 0))
        if (sx, sy + dy) not in obstacles:
            cand.append((0, dy))
        if cand:
            # prefer the move that reduces manhattan more
            bestm = None
            bestmd = None
            for mdx, mdy in cand:
                md = man(sx + mdx, sy + mdy, tx, ty)
                if bestmd is None or md < bestmd:
                    bestmd = md
                    bestm = (mdx, mdy)
            return [bestm[0], bestm[1]]
        return [0, 0]

    return [dx, dy]