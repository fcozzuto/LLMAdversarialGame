def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells") or to_set("unclaimed") or set()
    opp_terr = to_set("opponent_territory") or set()

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,0), (0,1), (1,-1), (1,0), (1,1)]
    best = None
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist_opp = abs(nx - ox) + abs(ny - oy)
        if unclaimed:
            d_unc = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in unclaimed)
        else:
            d_unc = abs(nx - w // 2) + abs(ny - h // 2)
        if opp_terr:
            d_oppterr = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in opp_terr)
        else:
            d_oppterr = dist_opp
        sc = (-d_unc) + 0.15 * dist_opp + 0.05 * d_oppterr
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    return best if best is not None else [0, 0]