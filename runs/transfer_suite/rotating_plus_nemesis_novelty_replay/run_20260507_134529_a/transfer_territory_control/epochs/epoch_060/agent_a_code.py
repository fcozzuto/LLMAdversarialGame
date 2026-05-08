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
    self_terr = to_set("self_territory")
    opp_terr = to_set("opponent_territory")
    unclaimed = to_set("unclaimed_cells")

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    opp_cells = opp_terr
    self_cells = self_terr if self_terr else {(sx, sy)}
    frontier_opp = set()
    for (x, y) in opp_cells:
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                frontier_opp.add((nx, ny))

    def mindist(pt_set, px, py):
        if not pt_set:
            return 10**9
        best = 10**9
        for tx, ty in pt_set:
            d = abs(tx - px) + abs(ty - py)
            if d < best:
                best = d
        return best

    # Try to counterclaim: move into opponent territory if possible; otherwise enter cells that are adjacent to opponent territory
    # or that reduce distance to opponent frontier while avoiding giving up safe expansion.
    best = None
    best_val = -10**18
    for dx, dy, nx, ny in candidates:
        if (nx, ny) in opp_cells:
            val = 5.0  # immediate flip target
        elif (nx, ny) in unclaimed or (nx, ny) not in self_cells and (nx, ny) not in obstacles:
            # prefer claiming near opponent
            val = 1.5
        else:
            val = 0.1

        if (nx, ny) in frontier_opp:
            val += 2.2
        else:
            val -= 0.1

        # keep pressure: closer to opponent position helps counterclaim
        d_opp = abs(nx - ox) + abs(ny - oy)
        val += (16 - d_opp) * 0.05

        # avoid stepping too deep into empty regions away from opponent
        d_self = mindist(self_cells, nx, ny)
        val -= d_self * 0.02

        # discourage moving into opponent territory corners if not directly on it (useful only when opponent near)
        if opp_cells:
            d_to_opp = mindist(opp_cells, nx, ny)
            val -= d_to_opp * 0.03

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]