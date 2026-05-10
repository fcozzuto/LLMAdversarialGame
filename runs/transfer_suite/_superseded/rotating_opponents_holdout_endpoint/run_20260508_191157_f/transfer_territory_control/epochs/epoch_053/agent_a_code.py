def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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
    opp_count = int(observation.get("opponent_territory_count", 0) or 0)
    self_count = int(observation.get("self_territory_count", 0) or 0)

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 5000
        if (nx, ny) in opp:
            # flipping opponent territory is valuable; scale up if we're behind
            score += 2200 + (0.6 * max(0, opp_count - self_count))

        # Encourage moving toward edges/frontier and away from being far from available cells
        dist_center = abs(nx - cx) + abs(ny - cy)
        score += -2.5 * dist_center

        # Small lookahead (depth 2) to prefer moves that reach/attack nearby cells sooner
        frontier = [(nx, ny)]
        visited = {(nx, ny)}
        local_best = 0
        for _ in range(2):
            new_front = []
            for x, y in frontier:
                for ddx, ddy in dirs:
                    tx, ty = x + ddx, y + ddy
                    if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in blocked or (tx, ty) in visited:
                        continue
                    visited.add((tx, ty))
                    if (tx, ty) in unclaimed:
                        local_best = max(local_best, 2500)
                    if (tx, ty) in opp:
                        local_best = max(local_best, 2000)
                    new_front.append((tx, ty))
            frontier = new_front
            if not frontier:
                break
        score += local_best

        # Prefer moves that reduce distance to nearest unclaimed if available
        if unclaimed:
            nearest = min(unclaimed, key=lambda p: abs(p[0] - nx) + abs(p[1] - ny))
            score += -1.8 * (abs(nearest[0] - nx) + abs(nearest[1] - ny))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]