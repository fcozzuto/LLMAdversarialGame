def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    self_cells = set(tuple(c) for c in (observation.get("self_territory") or []))
    opp_cells = set(tuple(c) for c in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(c) for c in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    frontier = set()
    if self_cells and unclaimed:
        for ux, uy in unclaimed:
            for dx, dy in neigh:
                if (ux + dx, uy + dy) in self_cells:
                    frontier.add((ux, uy))
                    break

    target_set = frontier if frontier else unclaimed
    def mindist(a, bset):
        best = None
        ax, ay = a
        for bx, by in bset:
            d = abs(ax - bx) + abs(ay - by)
            if best is None or d < best:
                best = d
        return best if best is not None else 999

    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 7
        elif (nx, ny) in opp_cells:
            score += 5
        elif (nx, ny) in self_cells:
            score += 0

        if target_set:
            score += -0.9 * mindist((nx, ny), target_set)

        # Slight pressure to avoid giving sweeper a closer access route
        score += 0.05 * (abs(nx - ox) + abs(ny - oy))

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]