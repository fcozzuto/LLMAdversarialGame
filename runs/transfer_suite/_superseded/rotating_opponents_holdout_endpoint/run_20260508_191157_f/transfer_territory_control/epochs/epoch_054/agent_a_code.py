def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    ox, oy = int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                unclaimed.add((x, y))

    opp = set()
    for p in (observation.get("opponent_territory") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                opp.add((x, y))

    if not unclaimed and not opp:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (0, 0)
    best_score = -10**18
    turn = int(observation.get("turn_index", 0) or 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        # Prefer center capture; prefer flipping opponent territory; avoid giving opponent closer access.
        dist_center = abs(nx - cx) + abs(ny - cy)
        dist_opp = abs(nx - ox) + abs(ny - oy)
        score = -dist_center + 0.12 * dist_opp

        if (nx, ny) in opp:
            score += 6.0  # strong flip pressure
        if (nx, ny) in unclaimed:
            score += 2.0  # claim opportunities

        # Slightly advance earlier; later focus on consolidation near center.
        if turn < 40:
            score += 0.15 * dist_center * (-1)
        else:
            score += 0.05 * (-dist_center)

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]