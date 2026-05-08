def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def mind(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose a primary target: nearest opponent territory if any, else best unclaimed from center.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    if opp_terr:
        tx, ty = min(opp_terr, key=lambda p: mind(sx, sy, p[0], p[1]))
    else:
        if unclaimed:
            tx, ty = min(unclaimed, key=lambda p: mind(cx, cy, p[0], p[1]) * 2 + mind(sx, sy, p[0], p[1]))
        else:
            tx, ty = cx, cy

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            score = -10**12 + (dx == 0 and dy == 0)
        else:
            score = 0
            if (nx, ny) in opp_terr:
                score += 1200
            elif (nx, ny) in unclaimed:
                score += 140
            elif (nx, ny) in self_terr:
                score += 40
            else:
                score += 10

            score += (mind(ox, oy, nx, ny) - mind(ox, oy, sx, sy)) * -8  # move away or toward? prefer closer to opponent if possible via territory
            score += (mind(sx, sy, tx, ty) - mind(nx, ny, tx, ty)) * 18        # closer to target is better
            # Encourage heading to boundary by preferring cells not already deep inside own territory
            if (nx, ny) not in self_terr:
                score += 15
            else:
                score -= 6

            # If we're adjacent to opponent territory, strongly prefer stepping into it
            for ax, ay in dirs:
                axx, ayy = nx + ax, ny + ay
                if inb(axx, ayy) and (axx, ayy) in opp_terr:
                    score += 25
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best