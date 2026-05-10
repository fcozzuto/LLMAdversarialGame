def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    frontier = []
    for x, y in unclaimed:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_terr:
                    frontier.append((x, y))
                    dx = dy = 2  # break both loops
                    break
            if not frontier or frontier[-1] != (x, y):
                continue
            if len(frontier) and frontier[-1] == (x, y):
                # we already broke outer dy loop via dx/dy hack
                break
        if frontier and frontier[-1] == (x, y) and (x, y) in unclaimed:
            pass
    if not frontier:
        frontier = list(unclaimed)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in opp_terr:
            score += 12
        elif (nx, ny) in unclaimed:
            score += 7
        elif (nx, ny) in self_terr:
            score += 2

        if frontier:
            score += -min(manh((nx, ny), t) for t in frontier)
        else:
            score += -manh((nx, ny), (ox, oy))

        if dx == 0 and dy == 0:
            score -= 0.5  # prefer movement
        if (score, -dx, -dy) > (best[0], -best[1], -best[2]):
            best = (score, dx, dy)

    if best[0] < -10**8:
        return [0, 0]
    return [int(best[1]), int(best[2])]