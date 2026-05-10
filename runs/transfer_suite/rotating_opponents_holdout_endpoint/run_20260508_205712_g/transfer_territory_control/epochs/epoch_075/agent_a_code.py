def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    unclaimed = set()
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                unclaimed.add((x, y))

    oppT = set()
    for p in (observation.get("opponent_territory") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                oppT.add((x, y))

    selfT = set()
    for p in (observation.get("self_territory") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                selfT.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = (-(10**9), 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        score = 0
        if cell in unclaimed:
            score += 120
        elif cell in oppT:
            score += 80
        elif cell in selfT:
            score += 10
        else:
            score += 5

        dist_center = abs(nx - cx) + abs(ny - cy)
        score -= int(dist_center * 0.5)

        # Prefer moves that decrease distance to nearest unclaimed/opp territory on the local frontier.
        if unclaimed:
            mind = 10**9
            for tx, ty in unclaimed:
                d = abs(tx - nx) + abs(ty - ny)
                if d < mind:
                    mind = d
            score -= min(40, mind)
        elif oppT:
            mind = 10**9
            for tx, ty in oppT:
                d = abs(tx - nx) + abs(ty - ny)
                if d < mind:
                    mind = d
            score -= min(40, mind)

        if score > best[0]:
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]