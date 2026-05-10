def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_ter = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    # Candidate targets: unclaimed cells adjacent to our territory (frontier)
    frontier = []
    for (x, y) in self_ter:
        for dx, dy in dirs:
            tx, ty = x + dx, y + dy
            if (tx, ty) in unclaimed:
                frontier.append((tx, ty))
    frontier = list(set(frontier))

    def score_target(tx, ty):
        # Prefer frontier expansion, avoid obstacles, and keep distance from opponent
        man_to_self = abs(tx - sx) + abs(ty - sy)
        man_to_opp = abs(tx - ox) + abs(ty - oy)
        # If this target is near opponent territory, penalize (likely contested)
        near_opp = 0
        for dx, dy in dirs:
            if (tx + dx, ty + dy) in opp_ter:
                near_opp = 1
                break
        # Small penalty if target is adjacent to obstacles (paths get blocked)
        near_obs = 0
        for dx, dy in dirs:
            if (tx + dx, ty + dy) in obstacles:
                near_obs = 1
                break
        return (0 if (tx, ty) in frontier else 10_000) + man_to_self + (0 if man_to_opp >= 6 else (7 - min(7, man_to_opp))) * 2 + near_obs * 3 + near_opp * 6

    targets = frontier if frontier else list(unclaimed)
    if not targets:
        return [0, 0]

    # Choose best target deterministically
    best = None
    for t in targets:
        tx, ty = t
        s = score_target(tx, ty)
        if best is None or s < best[0]:
            best = (s, tx, ty)
    _, tx, ty = best

    # Choose move that reduces distance to target and avoids stepping onto obstacle if possible
    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        val = (abs(tx - nx) + abs(ty - ny), abs(ox - nx) + abs(oy - ny))
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move