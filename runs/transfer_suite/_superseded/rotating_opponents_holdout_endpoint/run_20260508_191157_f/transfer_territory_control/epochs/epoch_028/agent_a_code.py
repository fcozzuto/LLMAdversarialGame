def choose_move(observation):
    w = observation.get("grid_width")
    h = observation.get("grid_height")
    if not isinstance(w, int) or not isinstance(h, int) or w <= 0 or h <= 0:
        return [0, 0]
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = observation.get("obstacles") or []
    obs = {(x, y) for x, y in obstacles if isinstance(x, int) and isinstance(y, int)}
    self_terr = {(x, y) for x, y in (observation.get("self_territory") or []) if isinstance(x, int) and isinstance(y, int)}
    opp_terr = {(x, y) for x, y in (observation.get("opponent_territory") or []) if isinstance(x, int) and isinstance(y, int)}
    unclaimed = {(x, y) for x, y in (observation.get("unclaimed_cells") or []) if isinstance(x, int) and isinstance(y, int)}

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h

    def adj_to_self(x, y):
        if not self_terr: return False
        for dx, dy in neigh4:
            if (x + dx, y + dy) in self_terr:
                return True
        return False

    def best_unclaimed_dist(x, y):
        if not unclaimed: return None
        md = None
        for ux, uy in unclaimed:
            d = (ux - x) * (ux - x) + (uy - y) * (uy - y)
            if md is None or d < md:
                md = d
        return md

    opp_target = None
    if opp_terr:
        opp_target = (sum(x for x, y in opp_terr) // len(opp_terr), sum(y for x, y in opp_terr) // len(opp_terr))
    else:
        opp_target = (ox, oy)

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue
        if (nx, ny) in unclaimed and adj_to_self(nx, ny):
            score = 10_000 - ((ox - nx) * (ox - nx) + (oy - ny) * (oy - ny))
        elif (nx, ny) in unclaimed:
            d = best_unclaimed_dist(nx, ny)
            score = 3000 - (d if d is not None else 0)
        else:
            tx, ty = opp_target
            score = -((tx - nx) * (tx - nx) + (ty - ny) * (ty - ny))
            if adj_to_self(nx, ny):
                score += 50
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]