def choose_move(observation):
    sx, sy = observation["self_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    self_count = int(observation.get("self_territory_count", 0) or 0)
    opp_count = int(observation.get("opponent_territory_count", 0) or 0)
    aggressive = self_count <= opp_count

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def mindist_opp(x, y):
        if not opp_terr: return abs(x - ox) + abs(y - oy)
        md = 10**9
        for tx, ty in opp_terr:
            d = abs(x - tx) + abs(y - ty)
            if d < md: md = d
        return md

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        dO = abs(nx - ox) + abs(ny - oy)
        dOppTerr = mindist_opp(nx, ny)
        if cell in opp_terr:
            score = 5000 - dO
        elif cell in unclaimed:
            score = 400 - (dO if aggressive else -dO) - 2 * dOppTerr
        elif cell in self_terr:
            score = 200 - (dO if aggressive else -dO) - dOppTerr
        else:
            score = 0 - (dO if aggressive else -dO)
        # discourage moving away from opponent when aggressive; discourage moving into opponent when defensive
        score += (-5 * dOppTerr if aggressive else 5 * dOppTerr)
        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best if best is not None else [0, 0]