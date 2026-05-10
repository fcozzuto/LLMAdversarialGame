def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)
    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))
    obstacles = set((int(x), int(y)) for x, y in (observation.get("obstacles") or []))

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    # Find frontier unclaimed cells adjacent to opponent territory (most valuable for claim/flip)
    opp_adj = []
    for (x, y) in unclaimed:
        if (x - 1, y) in opp_terr or (x + 1, y) in opp_terr or (x, y - 1) in opp_terr or (x, y + 1) in opp_terr or \
           (x - 1, y - 1) in opp_terr or (x + 1, y + 1) in opp_terr or (x - 1, y + 1) in opp_terr or (x + 1, y - 1) in opp_terr:
            opp_adj.append((x, y))

    # If no frontier, head toward nearest unclaimed; else toward nearest opponent cell
    targets = opp_adj
    if not targets:
        if unclaimed:
            targets = list(unclaimed)
        elif opp_terr:
            targets = list(opp_terr)

    def best_dist(x, y):
        if not targets: return 0
        best = None
        for (tx, ty) in targets:
            d = abs(tx - x) + abs(ty - y)
            if best is None or d < best: best = d
        return best if best is not None else 0

    # Obstacle-avoid; also discourage stepping into opponent if can instead approach frontier
    best_move = (0, 0)
    best_score = None
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0

        cell_score = 0
        if (nx, ny) in opp_terr:
            cell_score += 6  # likely flip on entry
        elif (nx, ny) in self_terr:
            cell_score += 1
        elif (nx, ny) in unclaimed:
            # claiming unclaimed is good; frontier-adjacent more so
            if (nx - 1, ny) in opp_terr or (nx + 1, ny) in opp_terr or (nx, ny - 1) in opp_terr or (nx, ny + 1) in opp_terr or \
               (nx - 1, ny - 1) in opp_terr or (nx + 1, ny + 1) in opp_terr or (nx - 1, ny + 1) in opp_terr or (nx + 1, ny - 1) in opp_terr:
                cell_score += 4
            else:
                cell_score += 2

        d = best_dist(nx, ny)
        # Prefer getting closer to the main target; slight penalty for moving away
        approach = -d
        # Discourage illegal stagnation if we have a meaningful target
        stagn = -2 if (dx == 0 and dy == 0 and targets) else 0

        score = cell_score + approach + stagn
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]