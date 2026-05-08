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
    resources = to_set("resources")
    unclaimed = to_set("unclaimed_cells")
    opp_terr = to_set("opponent_territory")
    self_terr = to_set("self_territory")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_to_opp(x, y):
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) in opp_terr:
                return True
        return False

    # Prefer capturing opponent directly; otherwise take unclaimed cells next to opponent.
    # Tie-break: reduce distance to opponent, avoid stepping onto own territory if possible.
    best = (-(10**9), 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        val = 0.0
        if (nx, ny) in opp_terr:
            val += 10.0
        elif (nx, ny) in unclaimed:
            val += 4.0 if adj_to_opp(nx, ny) else 2.0
        elif (nx, ny) in self_terr:
            val -= 1.0
        else:
            val -= 0.2

        if (nx, ny) in resources:
            val += 2.0

        dist_opp = abs(nx - ox) + abs(ny - oy)
        val += -0.1 * dist_opp
        if (nx, ny) in self_terr:
            val += -0.05  # slight deterrent

        # Deterministic tie-breaker
        tieb = (val, -dist_opp, -(1 if (nx, ny) in self_terr else 0), -dx, -dy)
        if tieb > best:
            best = tieb
    return [best[3] if best[3] in (-1, 0, 1) else 0, best[4] if best[4] in (-1, 0, 1) else 0]