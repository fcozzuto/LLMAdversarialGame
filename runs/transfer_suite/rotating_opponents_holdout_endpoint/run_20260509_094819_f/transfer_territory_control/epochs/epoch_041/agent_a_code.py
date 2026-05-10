def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    oppx, oppy = observation.get("opponent_position", [w - 1, h - 1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def dman(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Find a local frontier cell near us to expand into (unclaimed adjacent to our territory).
    frontier = []
    for (x, y) in uncla:
        if dman(x, y, sx, sy) > 4: 
            continue
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x + ax, y + ay
            if (nx, ny) in selfT:
                frontier.append((x, y))
                break
    frontier = frontier[:10]

    best_move = [0, 0]
    bestv = -10**18

    # Simple deterministic tie-break order by dirs sequence.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = -2
        if (nx, ny) in obstacles:
            v -= 10**6
        if (nx, ny) in oppT:
            v += 180  # entering opponent territory flips control
            v += -dman(nx, ny, sx, sy)
        if (nx, ny) in selfT:
            v += 6
        if (nx, ny) in uncla:
            v += 30
            # prefer moving into cells that are adjacent to our territory
            for ax, ay in ((1,0),(-1,0),(0,1),(0,-1)):
                if (nx + ax, ny + ay) in selfT:
                    v += 40
                    break

        # Goal pressure: closer to frontier or farther from opponent.
        if frontier:
            d = min(dman(nx, ny, fx, fy) for (fx, fy) in frontier)
            v += 25 - 4 * d
        else:
            v += -dman(nx, ny, oppx, oppy) * 2

        # Avoid drifting into dead corners unless it improves distance to frontier/center.
        centerx, centery = (w - 1) / 2, (h - 1) / 2
        v += -0.2 * ((nx - centerx) ** 2 + (ny - centery) ** 2)

        if v > bestv:
            bestv = v
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]