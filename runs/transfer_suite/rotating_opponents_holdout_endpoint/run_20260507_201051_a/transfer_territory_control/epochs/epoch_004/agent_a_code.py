def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    opp_pos = observation.get("opponent_position", (0, 0))
    ox, oy = opp_pos[0], opp_pos[1]

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory", []) or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells", []) or []))
    resources = set(tuple(p) for p in (observation.get("resources", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    opp_targets = list(opp_terr) if opp_terr else []
    nearest_opp = None
    if opp_targets:
        nearest_opp = min(opp_targets, key=lambda p: md(sx, sy, p[0], p[1]))

    best = None
    best_score = -10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            score = -1000
        else:
            score = 0
            cell = (nx, ny)
            if cell in opp_terr:
                score += 80
            elif cell in unclaimed:
                score += 6
                if opp_targets:
                    score += max(0, 10 - md(nx, ny, nearest_opp[0], nearest_opp[1])) * 0.6
                score += max(0, 6 - md(nx, ny, ox, oy)) * 0.2
            elif cell in self_terr:
                score += 3
                if opp_targets:
                    score += max(0, 8 - md(nx, ny, nearest_opp[0], nearest_opp[1])) * 0.2
            else:
                score += 1

            if cell in resources:
                score += 12

            # Prefer approaching center slightly to keep mobility
            score -= 0.03 * (abs(nx - cx) + abs(ny - cy))

            # If no opponent territory known, move toward unclaimed/resources/opponent
            if not opp_targets:
                if unclaimed:
                    near_u = min(unclaimed, key=lambda p: md(nx, ny, p[0], p[1]))
                    score += max(0, 8 - md(nx, ny, near_u[0], near_u[1])) * 0.4
                else:
                    score += max(0, 8 - md(nx, ny, ox, oy)) * 0.25

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]