def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = sorted(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    samples = unclaimed[:10] if len(unclaimed) > 10 else unclaimed

    best = None
    bestv = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            tx, ty = sx + dx, sy + dy
            if not inb(tx, ty) or (tx, ty) in obstacles:
                tx, ty = sx, sy
                dx, dy = 0, 0
            t = (tx, ty)

            if t in opp_terr:
                claim = 4.0
            elif t in unclaimed:
                claim = 2.0
            elif t in self_terr:
                claim = 0.5
            else:
                claim = 0.0

            if samples:
                mindu = None
                for ux, uy in samples:
                    d = manh(tx, ty, ux, uy)
                    mindu = d if mindu is None or d < mindu else mindu
                near = -0.08 * mindu
            else:
                near = 0.0

            sep = -0.04 * manh(tx, ty, ox, oy)
            v = claim + near + sep

            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)

    return [best[0], best[1]]