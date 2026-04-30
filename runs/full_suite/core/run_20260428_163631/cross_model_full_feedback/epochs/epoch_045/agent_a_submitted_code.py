def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for p in observation.get("resources", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    best = None
    if resources:
        for dx, dy, nx, ny in legal:
            d = min(manh(nx, ny, rx, ry) for rx, ry in resources)
            # Tie-break deterministically by (d, -resource-richness, dx, dy)
            score = (d, -min(1, len(resources)), dx, dy)
            if best is None or score < best[0]:
                best = (score, (dx, dy))
    else:
        for dx, dy, nx, ny in legal:
            # No resources: stay away from opponent to reduce their advantage
            d_opp = man(nx, ny, ox, oy)
            score = (-d_opp, dx, dy)
            if best is None or score < best[0]:
                best = (score, (dx, dy))

    return [int(best[1][0]), int(best[1][1])]