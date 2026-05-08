def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    self_t = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_t = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def neigh8(x, y):
        for dx, dy in dirs:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                yield nx, ny

    # Prefer: move into opponent territory (flip) or into unclaimed adjacent to opponent territory.
    opp_neighbors = set()
    for x, y in opp_t:
        for nx, ny in neigh8(x, y):
            if (nx, ny) in unclaimed:
                opp_neighbors.add((nx, ny))
    targets = list(opp_neighbors) if opp_neighbors else (list(unclaimed) if unclaimed else list(opp_t))

    def best_target():
        if not targets:
            return None
        best = None
        best_d = 10**9
        best_man = 10**9
        for tx, ty in targets:
            d = (tx - sx) ** 2 + (ty - sy) ** 2
            # favor closer, then favor x to break ties deterministically
            man = abs(tx - sx) + abs(ty - sy)
            if d < best_d or (d == best_d and (man < best_man or (man == best_man and (tx, ty) < best))):
                best_d, best_man, best = d, man, (tx, ty)
        return best

    target = best_target()

    cur_score = len(self_t)
    opp_score = len(opp_t)

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = 0
        if (nx, ny) in opp_t:
            # Flipping on entry; strong immediate value.
            val += 1000 + 2 * opp_score
            # Slight preference for hitting closer to opponent position.
            val += max(0, 30 - (abs(nx - ox) + abs(ny - oy)))
        elif (nx, ny) in unclaimed:
            val += 50
            # If this unclaimed cell is adjacent to opponent territory, prioritize it.
            if (nx, ny) in opp_neighbors:
                val += 200
        elif (nx, ny) in self_t:
            val += 5

        if target is not None:
            # Move toward target.
            val += 40 - (abs(nx - target[0]) + abs(ny - target[1]))

        # Deterministic tie-break: prefer moves in fixed dir order (dirs list order).
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]