def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    tx, ty = ox, oy  # push toward opponent corner/territory
    best = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_target = abs(nx - tx) + abs(ny - ty)
        d_enemy = abs(nx - ox) + abs(ny - oy)

        score = 0
        score += -d_target * 6
        if (nx, ny) in self_terr:
            score += 60
        if (nx, ny) in unclaimed:
            score += 18
        if (nx, ny) in opp_terr:
            score += 700  # flipping on entry enabled: contest and take space
        if d_enemy <= 1:
            score += 25  # being near the sweeper helps during contests
        if (nx, ny) in obstacles:
            score -= 10**6

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]