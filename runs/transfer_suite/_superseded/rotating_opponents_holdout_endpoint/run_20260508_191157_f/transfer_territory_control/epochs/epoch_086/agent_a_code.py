def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opp_frontier = set()
    for ox, oy in oppT:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = ox + dx, oy + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and (nx, ny) in unclaimed:
                    opp_frontier.add((nx, ny))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    best = None
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        cell = (nx, ny)

        score = 0.0
        if cell in selfT:
            score += 0.05
        elif cell in oppT:
            score += 2.2
        elif cell in unclaimed:
            score += 1.1
        else:
            score += 0.2  # neutral/other

        score += 0.25 * (1.0 / (1.0 + ((nx - cx) ** 2 + (ny - cy) ** 2)))

        if opp_frontier:
            # favor moving closer to unclaimed adjacent to opponent territory
            dmin = 10**9
            for tx, ty in opp_frontier:
                dd = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
                if dd < dmin:
                    dmin = dd
            score += 0.8 * (1.0 / (1.0 + dmin))
        else:
            # otherwise push toward center
            score += 0.2 * (1.0 / (1.0 + ((nx - cx) ** 2 + (ny - cy) ** 2)))

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]