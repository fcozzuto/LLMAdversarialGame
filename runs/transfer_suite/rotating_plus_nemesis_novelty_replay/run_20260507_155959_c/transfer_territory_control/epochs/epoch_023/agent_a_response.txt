def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = (observation.get("self_position", [0, 0]) + [0, 0])[:2]
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    self_cells = set(tuple(xy) for xy in (observation.get("self_territory", []) or []))
    opp_cells = set(tuple(xy) for xy in (observation.get("opponent_territory", []) or []))
    unclaimed = set(tuple(xy) for xy in (observation.get("unclaimed_cells", []) or []))
    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose best next step by local territory-control potential.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) in self_cells:
            base = 1
        elif (nx, ny) in opp_cells:
            base = 250  # flipping on entry
        elif (nx, ny) in unclaimed:
            base = 80
        else:
            base = 10  # likely already ours/unknown; keep moving

        # Reward taking cells that are adjacent to opponent territory (frontier pressure).
        adj_opp = 0
        for ddx, ddy in neigh8:
            ax, ay = nx + ddx, ny + ddy
            if inb(ax, ay) and (ax, ay) in opp_cells:
                adj_opp += 1
        frontier = adj_opp * 25

        # If opponent is near, move toward their centroid / pressure zone.
        if opp_cells:
            ocx = sum(x for x, _ in opp_cells) // len(opp_cells)
            ocy = sum(y for _, y in opp_cells) // len(opp_cells)
            dist_before = abs(sx - ocx) + abs(sy - ocy)
            dist_after = abs(nx - ocx) + abs(ny - ocy)
            approach = (dist_before - dist_after) * 8
        else:
            approach = 0

        # Prefer unclaimed that are near many opponent cells.
        near_unclaimed_front = 0
        if (nx, ny) in unclaimed:
            for ddx, ddy in neigh8:
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay) and (ax, ay) in opp_cells:
                    near_unclaimed_front += 1
        unclaimed_front = near_unclaimed_front * 35

        score = base + frontier + approach + unclaimed_front
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    # Deterministic fallback: if somehow no valid moves, stay.
    dx, dy = best_move
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]