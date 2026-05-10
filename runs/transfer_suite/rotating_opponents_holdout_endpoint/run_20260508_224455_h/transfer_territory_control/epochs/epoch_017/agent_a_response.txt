def choose_move(observation):
    sx, sy = observation["self_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    ox, oy = observation["opponent_position"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def neigh8(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx != 0 or dy != 0:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        yield nx, ny

    # Pick targets: unclaimed near opponent first, else near our own, else any unclaimed, else opponent position.
    targets = []
    if unclaimed and opp_t:
        for x, y in unclaimed:
            for nx, ny in neigh8(x, y):
                if (nx, ny) in opp_t:
                    targets.append((x, y))
                    break
    if not targets and unclaimed:
        if self_t:
            for x, y in unclaimed:
                for nx, ny in neigh8(x, y):
                    if (nx, ny) in self_t:
                        targets.append((x, y))
                        break
        if not targets:
            targets = list(unclaimed)
    if not targets:
        targets = [(ox, oy)]

    # Deterministic nearest target function
    def nearest_dist_to_targets(x, y):
        best = None
        for tx, ty in targets:
            d = abs(tx - x) + abs(ty - y)
            if best is None or d < best:
                best = d
        return best if best is not None else 0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)

        # Base gain
        if cell in opp_t:
            score = 18
        elif cell in unclaimed:
            score = 12
        elif cell in self_t:
            score = 3
        else:
            score = 0

        # Shaping: go towards targets
        d_t = nearest_dist_to_targets(nx, ny)
        score += -2.2 * d_t

        # Safety shaping against sweeper: prefer moving away from opponent slightly
        d_o = abs(nx - ox) + abs(ny - oy)
        score += 0.35 * d_o

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]