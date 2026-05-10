def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation.get("opponent_position", (x, y))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    if not unclaimed and not oppT:
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    max_check = 30
    unclaimed_check = unclaimed[:max_check] if unclaimed else []

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0

        if unclaimed_check:
            dmin = 10**9
            for p in unclaimed_check:
                px, py = p
                d = manh(nx, ny, px, py)
                if d < dmin:
                    dmin = d
            score += 200 - 10 * dmin
            if (nx, ny) in set(unclaimed_check):
                score += 300
        else:
            score += 120 - 10 * manh(nx, ny, ox, oy)

        if (nx, ny) in oppT:
            score += 250
        if (nx, ny) in selfT:
            score -= 5

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best