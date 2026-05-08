def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if p and len(p) >= 2)
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if p and len(p) >= 2)
    unclaimed = [(int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if p and len(p) >= 2 and (int(p[0]), int(p[1])) not in obstacles]
    opp_pos = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(opp_pos[0]), int(opp_pos[1])

    dirs = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    def neigh(x, y):
        for dx, dy in dirs[1:]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                yield nx, ny

    target_un = None
    if unclaimed:
        # Prefer closer unclaimed that is near opponent territory to force expansion/contact.
        opp_list = list(opp_terr) if opp_terr else [(ox, oy)]
        best = None
        for ux, uy in unclaimed:
            d = abs(ux - sx) + abs(uy - sy)
            dopp = min(abs(ux - px) + abs(uy - py) for px, py in opp_list) if opp_list else d
            score = (d + max(0, dopp - 1), d, ux, uy)
            if best is None or score < best[0]:
                best = (score, (ux, uy))
        target_un = best[1]

    def move_value(nx, ny):
        if (nx, ny) in obstacles:
            return -10**9
        v = 0
        if (nx, ny) in opp_terr:
            v += 120  # immediate flip/pressure
        elif (nx, ny) in unclaimed:
            v += 55
        elif (nx, ny) in self_terr:
            v += 8
        else:
            v += 2
        # Prefer moves that increase contact with opponent territory.
        adj = 0
        for ax, ay in neigh(nx, ny):
            if (ax, ay) in opp_terr:
                adj += 1
        v += adj * 12
        # Path shaping: move toward either chosen unclaimed or opponent.
        if target_un is not None:
            v += max(0, 20 - (abs(nx - target_un[0]) + abs(ny - target_un[1])))
        else:
            v += max(0, 18 - (abs(nx - ox) + abs(ny - oy)))
        # Mild preference for staying away from corners/edges obstacles? keep deterministic: small edge bonus for territory.
        edge_bonus = (1 if nx in (0, w - 1) else 0) + (1 if ny in (0, h - 1) else 0)
        v += edge_bonus * 2
        return v

    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-break: lexicographic by dx,dy order in dirs
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        val = move_value(nx, ny)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]