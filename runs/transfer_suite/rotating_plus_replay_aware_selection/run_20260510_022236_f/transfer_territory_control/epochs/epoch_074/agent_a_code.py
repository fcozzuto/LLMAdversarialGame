def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    self_terr = set(map(tuple, observation.get("self_territory") or []))
    op_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = [tuple(map(int, c)) for c in (observation.get("unclaimed_cells") or []) if len(c) >= 2]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    # Choose a deterministic target cell
    if unclaimed:
        best = None
        for cx, cy in unclaimed:
            if (cx, cy) in obstacles:
                continue
            d = abs(cx - sx) + abs(cy - sy)
            cand = (d, cy, cx)
            if best is None or cand < best[0]:
                best = (cand, (cx, cy))
        goal = best[1] if best is not None else (sx, sy)
    else:
        # If nothing unclaimed, drift toward opponent territory or nearest free neighbor
        goal = (sx, sy)
        if op_terr:
            best = None
            for cx, cy in op_terr:
                d = abs(cx - sx) + abs(cy - sy)
                cand = (d, cy, cx)
                if best is None or cand < best[0]:
                    best = (cand, (cx, cy))
            goal = best[1] if best is not None else (sx, sy)

    gx, gy = goal
    # Evaluate candidate moves
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        # Base: move closer to goal
        dist_goal = abs(gx - nx) + abs(gy - ny)
        score = -dist_goal
        # Territory incentives
        if (nx, ny) in op_terr:
            score += 1200  # likely flipping on entry
        elif (nx, ny) in self_terr:
            score += 80
        else:
            # unclaimed bonus if stepping into it
            if (nx, ny) in set(unclaimed) if unclaimed else False:
                score += 300
            else:
                score += 10
        # Small preference for expanding toward center-ish lines (helps vs center-claim)
        cx, cy = w // 2, h // 2
        score += -(abs(cx - nx) + abs(cy - ny)) * 2

        # Deterministic tie-break
        cand = (score, -abs(dx), -abs(dy), dy, dx)
        if cand > (best_score, -abs(best_move[0]), -abs(best_move[1]), best_move[1], best_move[0]):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]