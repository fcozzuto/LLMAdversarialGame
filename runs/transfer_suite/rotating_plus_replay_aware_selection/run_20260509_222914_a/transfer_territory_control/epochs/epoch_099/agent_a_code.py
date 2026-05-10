def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    self_ter = set(tuple(p) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_ter = set(tuple(p) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def adj_counts(x, y):
        ao = 0
        aa_opp = 0
        aa_self = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if not inb(nx, ny): 
                    continue
                if (nx, ny) in obstacles: 
                    ao += 1
                if (nx, ny) in opp_ter: 
                    aa_opp += 1
                if (nx, ny) in self_ter: 
                    aa_self += 1
        return ao, aa_self, aa_opp

    best = [0, 0]
    bestv = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            v = -10_000
        else:
            ao, aa_self, aa_opp = adj_counts(nx, ny)
            v = 0
            if (nx, ny) in self_ter:
                v += 1
            elif (nx, ny) in opp_ter:
                v += 80 + 6 * aa_opp - 4 * ao  # flip by entering
            elif (nx, ny) in unclaimed:
                v += 60 + 10 * aa_self + 4 * aa_opp - 6 * ao
            else:
                v += 5 - 3 * ao  # neutral/unknown
            v += - (abs(nx - sx) + abs(ny - sy))  # stay close
        if bestv is None or v > bestv or (v == bestv and (dx, dy) < tuple(best)):
            bestv = v
            best = [dx, dy]

    if best[0] not in (-1, 0, 1) or best[1] not in (-1, 0, 1):
        return [0, 0]
    return best