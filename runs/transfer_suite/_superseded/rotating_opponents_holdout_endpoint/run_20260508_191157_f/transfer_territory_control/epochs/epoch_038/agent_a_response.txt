def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    opp_terr = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opp_terr.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells") or []
    unclaimed = [(int(x), int(y)) for x, y in unclaimed if 0 <= int(x) < w and 0 <= int(y) < h and (int(x), int(y)) not in blocked]
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Edge-pointing strategy vs center-claim: choose the farther edge-corner from opponent, but still press nearby unclaimed.
    edgeA = (w - 1, 0)
    edgeB = (0, h - 1)
    target_edge = edgeA if (edgeA[0] - ox) ** 2 + (edgeA[1] - oy) ** 2 >= (edgeB[0] - ox) ** 2 + (edgeB[1] - oy) ** 2 else edgeB

    def dist2(a, b):
        return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])

    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue

        score = -dist2((nx, ny), target_edge)

        # If we can directly flip into opponent territory, heavily reward.
        if (nx, ny) in opp_terr:
            score += 500.0

        # Otherwise, move toward the best nearby unclaimed cell; if none, drift toward the edge target.
        if unclaimed:
            dmin = 10**18
            for tx, ty in unclaimed:
                d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
                if d < dmin:
                    dmin = d
            score += -0.8 * dmin
        else:
            score += -0.05 * dist2((nx, ny), (ox, oy))

        # Slightly avoid stepping adjacent to opponent to reduce counter-flips.
        if abs(nx - ox) <= 1 and abs(ny - oy) <= 1:
            score -= 15.0

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move