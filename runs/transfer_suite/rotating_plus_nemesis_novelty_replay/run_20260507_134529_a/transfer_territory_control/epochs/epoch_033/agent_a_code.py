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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**18
    cx, cy = w // 2, h // 2

    def neighbors(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    yield (nx, ny)

    # Focus: pressure opponent counterclaims; aim to step onto opponent territory or onto cells adjacent to it,
    # while avoiding obstacles and not walking deep into the opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0.0
        if (nx, ny) in opp_terr:
            val += 3.0  # immediate flip value
        elif (nx, ny) in unclaimed:
            val += 0.6
        elif (nx, ny) in self_terr:
            val += 0.1

        # adjacency to opponent territory: likely to trigger counterclaim contests; stepping near it can flip on entry next
        adj_opp = 0
        for p in neighbors(nx, ny):
            if p in opp_terr:
                adj_opp += 1
        val += 0.35 * adj_opp

        # avoid entering areas dominated by opponent (more distance from opponent is safer when not flipping)
        dist_now = abs(nx - ox) + abs(ny - oy)
        val += 0.05 * dist_now

        # attract to central region slightly to prevent getting funneled
        val += -0.002 * (abs(nx - cx) + abs(ny - cy))

        # mild preference to expand outward from our current territory frontier
        if self_terr:
            adj_self = sum(1 for p in neighbors(nx, ny) if p in self_terr)
            val += 0.12 * adj_self

        # deterministic tie-break: lexicographic by move order
        if val > bestv + 1e-12 or (abs(val - bestv) <= 1e-12 and (dx, dy) < best):
            bestv = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]