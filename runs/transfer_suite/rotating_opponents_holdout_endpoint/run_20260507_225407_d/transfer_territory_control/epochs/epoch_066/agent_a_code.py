def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = observation.get("obstacles") or []
    occ = set()
    for p in obs:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                occ.add((x, y))

    def parse_key(key):
        out = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    unclaimed = parse_key("unclaimed_cells")
    opp_t = parse_key("opponent_territory")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in occ:
            continue

        sc = 0
        if (nx, ny) in unclaimed:
            sc += 500
        if (nx, ny) in opp_t:
            sc += 200

        if unclaimed:
            md = 10**9
            for ux, uy in unclaimed:
                d = (nx - ux) * (nx - ux) + (ny - uy) * (ny - uy)
                if d < md:
                    md = d
            sc += 200 - md
        else:
            sc += -((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))

        sc += -(dx * dx + dy * dy) * 0.1

        if best is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in occ:
                return [dx, dy]
        return [0, 0]
    return best