def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def to_set(key):
        out = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.add((x, y))
        return out

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose a target that is simultaneously hard for opponent and beneficial for us.
    candidates = list(unclaimed)
    if not candidates:
        candidates = list(self_terr) if self_terr else [(sx, sy)]
    best_t = (sx, sy)
    best_s = -10**18
    for tx, ty in candidates:
        if (tx, ty) in obstacles:
            continue
        ds = abs(tx - sx) + abs(ty - sy)
        do = abs(tx - ox) + abs(ty - oy)
        # Prefer cells far from opponent; also prefer being closer than opponent.
        sc = (do - ds * 0.9)
        if (tx, ty) in unclaimed:
            sc += 2.0
        if (tx, ty) in self_terr:
            sc -= 1.0
        if sc > best_s:
            best_s = sc
            best_t = (tx, ty)

    tx, ty = best_t
    best_move = (0, 0)
    best_mv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Greedy local evaluation: claim safe unclaimed; avoid stepping into opponent control.
        dn_o = abs(nx - ox) + abs(ny - oy)
        dn_s = abs(nx - sx) + abs(ny - sy)
        to_t = abs(tx - nx) + abs(ty - ny)
        mv = 0.0
        mv += dn_o * 1.2
        mv -= to_t * 0.7
        mv -= dn_s * 0.01
        if (nx, ny) in unclaimed:
            mv += 3.0
        if (nx, ny) in opp_terr:
            mv -= 8.0
        if (nx, ny) in self_terr:
            mv += 0.2  # mild preference to stabilize
        if mv > best_mv:
            best_mv = mv
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]