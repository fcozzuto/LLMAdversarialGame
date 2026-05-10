def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    self_terr_list = observation.get("self_territory", []) or []
    opp_terr_list = observation.get("opponent_territory", []) or []
    unclaimed_list = observation.get("unclaimed_cells", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    opp_x, opp_y = observation.get("opponent_position", [w - 1, h - 1])

    self_terr = set((int(p[0]), int(p[1])) for p in self_terr_list if isinstance(p, (list, tuple)) and len(p) == 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in opp_terr_list if isinstance(p, (list, tuple)) and len(p) == 2)
    unclaimed = set((int(p[0]), int(p[1])) for p in unclaimed_list if isinstance(p, (list, tuple)) and len(p) == 2)
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list if isinstance(p, (list, tuple)) and len(p) == 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Pick a deterministic "expansion anchor": closest edge unclaimed, else closest unclaimed, else opponent territory
    edge_unclaimed = [(x, y) for (x, y) in unclaimed if x in (0, w - 1) or y in (0, h - 1)]
    if edge_unclaimed:
        anchor = min(edge_unclaimed, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    elif unclaimed:
        anchor = min(unclaimed, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    elif opp_terr:
        anchor = min(opp_terr, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), t[0], t[1]))
    else:
        anchor = (opp_x, opp_y)

    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0.0
        if (nx, ny) in self_terr:
            score += 1.2
        elif (nx, ny) in unclaimed:
            score += 3.2
        elif (nx, ny) in opp_terr:
            score += 5.3  # flip enabled: contest is valuable

        dist_anchor_before = abs(sx - anchor[0]) + abs(sy - anchor[1])
        dist_anchor_after = abs(nx - anchor[0]) + abs(ny - anchor[1])
        score += 0.9 * (dist_anchor_before - dist_anchor_after)

        # Avoid getting "too close" to opponent in ways that likely let them sweep back
        dist_opp_after = max(0, abs(nx - opp_x) + abs(ny - opp_y))
        score -= 0.06 * dist_opp_after

        # Encourage moving to boundary cells when anchor is boundary
        if anchor[0] in (0, w - 1) or anchor[1] in (0, h - 1):
            if nx in (0, w - 1) or ny in (0, h - 1):
                score += 0.6

        # Deterministic tie-break: prefer smallest (dx,dy) lexicographically
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]