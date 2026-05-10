def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    selfT = set(tuple(p) for p in (observation.get("self_territory") or []))
    oppT = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    uncla = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    opp_list = list(oppT) if oppT else []
    un_list = list(uncla) if uncla else []

    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in oppT:
            score += 100000
        if (nx, ny) in uncla:
            score += 500
        if (nx, ny) in selfT:
            score += 50
        if un_list:
            d = min(abs(nx - ux) + abs(ny - uy) for ux, uy in un_list)
            score -= d
        if opp_list:
            do = min(abs(nx - ox) + abs(ny - oy) for ox, oy in opp_list)
            score -= 2 * do
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best