def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def parse_cells(key):
        out = set()
        cells = observation.get(key) or []
        for p in cells:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = parse_cells("obstacles")
    unclaimed = parse_cells("unclaimed_cells")
    opp_terr = parse_cells("opponent_territory")
    self_terr = parse_cells("self_territory")

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    opp_list = list(opp_terr)
    un_list = list(unclaimed)

    def dist(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    def best_for_target(tx, ty):
        dself = dist(sx, sy, tx, ty)
        dop = dist(ox, oy, tx, ty)
        gain = (1 if self_terr else 0) + (dop - dself)  # prefer targets closer to us than them
        if (tx, ty) in opp_terr:
            gain += 3
        if (tx, ty) in unclaimed:
            gain += 2
        return gain - dself * 0.1

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0.0
        if un_list:
            best = -1e9
            for tx, ty in un_list:
                if abs(tx - nx) + abs(ty - ny) <= max(w, h):
                    best = max(best, best_for_target(tx, ty) - dist(nx, ny, tx, ty) * 0.2)
            if best > -1e8:
                score += best
        if opp_list:
            md = 10**9
            for tx, ty in opp_list:
                dd = dist(nx, ny, tx, ty)
                if dd < md:
                    md = dd
            score += (md == 0) * 4 - md * 0.03
        if self_terr:
            # encourage staying near current territory to reduce risk
            md2 = 10**9
            for tx, ty in self_terr:
                dd2 = dist(nx, ny, tx, ty)
                if dd2 < md2:
                    md2 = dd2
            score += (2 if md2 == 0 else 0) - md2 * 0.02
        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = candidates[0]
    return [int(dx), int(dy)]