def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    def to_set(v):
        s = set()
        if isinstance(v, (list, tuple)):
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = p[0], p[1]
                    if isinstance(x, int) and isinstance(y, int):
                        s.add((x, y))
        return s

    unclaimed = to_set(observation.get("unclaimed_cells"))
    obstacles = to_set(observation.get("obstacles"))
    self_terr = to_set(observation.get("self_territory"))
    opp_terr = to_set(observation.get("opponent_territory"))

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    best = None
    best_score = -10**18

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    un_list = list(unclaimed) if unclaimed else []
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 2000
        if (nx, ny) in opp_terr:
            score -= 500
        if (nx, ny) in self_terr:
            score += 50
        score += (abs(nx - ox) + abs(ny - oy))  # prefer moving away deterministically
        if un_list:
            md = 10**9
            for ux, uy in un_list:
                d = abs(nx - ux) + abs(ny - uy)
                if d < md:
                    md = d
            score += max(0, 100 - md)  # closer to some unclaimed is better
        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = ax + dx, ay + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best