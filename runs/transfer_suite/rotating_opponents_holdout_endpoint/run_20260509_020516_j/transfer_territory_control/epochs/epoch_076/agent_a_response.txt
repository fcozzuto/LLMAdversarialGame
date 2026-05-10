def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < W and 0 <= by < H:
                blocked.add((bx, by))

    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    opp_set = set((int(x), int(y)) for x, y in opp_terr if x is not None and y is not None)
    self_set = set((int(x), int(y)) for x, y in self_terr if x is not None and y is not None)
    unclaimed = observation.get("unclaimed_cells") or []
    un_set = set((int(x), int(y)) for x, y in unclaimed if x is not None and y is not None)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in blocked

    # Defense/offense switch: if behind, push hard toward opponent-adjacent unclaimed.
    sc_self = int(observation.get("self_territory_count", len(self_set)) or 0)
    sc_opp = int(observation.get("opponent_territory_count", len(opp_set)) or 0)
    behind = sc_self <= sc_opp
    turn = int(observation.get("turn_index", 0) or 0)

    if self_set:
        cx = sum(x for x, _ in self_set) / float(len(self_set))
        cy = sum(y for _, y in self_set) / float(len(self_set))
    else:
        cx, cy = sx, sy

    def adj_to_opp(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in opp_set:
                    return True
        return False

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        val = 0.0
        if (nx, ny) in opp_set:
            val += 100.0
        elif (nx, ny) in un_set:
            val += 10.0
            if adj_to_opp(nx, ny):
                val += 7.0
        elif (nx, ny) in self_set:
            val += 1.0

        # If leading, defend centroid; if trailing, prefer advancing.
        dist_cent = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        val += (-0.015) * dist_cent if not behind else (0.002) * dist_cent

        # Deterministic phase nudge to break symmetry
        if (turn % 2) == 0:
            val += 0.001 * (nx + 2 * ny)
        else:
            val += 0.001 * (2 * nx - ny)

        if best is None or val > best[0] or (val == best[0] and (dx, dy) < best[1]):
            best = (val, (dx, dy))

    if best is None:
        return [0, 0]
    return [best[1][0], best[1][1]]