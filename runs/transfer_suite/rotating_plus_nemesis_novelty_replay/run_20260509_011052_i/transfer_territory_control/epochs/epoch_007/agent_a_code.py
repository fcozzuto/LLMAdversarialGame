def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    self_terr = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory", []) or []))
    opp_terr = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells", []) or []))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    self_count = int(observation.get("self_territory_count", len(self_terr)))
    opp_count = int(observation.get("opponent_territory_count", len(opp_terr)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    opp_pos = observation.get("opponent_position", (sx, sy))
    ax, ay = int(opp_pos[0]), int(opp_pos[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -1e18
    aggressive = 1 if self_count >= opp_count else -1

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in opp_terr:
            cell_score = 12 + (6 if aggressive > 0 else 0)
        elif (nx, ny) in unclaimed:
            cell_score = 9 + (3 if aggressive < 0 else 0)
        elif (nx, ny) in self_terr:
            cell_score = 4
        else:
            cell_score = 1

        center_dist = abs(nx - cx) + abs(ny - cy)
        center_score = -center_dist * 0.6

        dist_to_opp = abs(nx - ax) + abs(ny - ay)
        opp_dist_score = (-dist_to_opp * 0.15) + (dist_to_opp * 0.03 if aggressive < 0 else 0)

        adj_opp = 0
        for ddx, ddy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty) and (tx, ty) in opp_terr:
                adj_opp += 1
        adj_bonus = (adj_opp * (2.2 if aggressive > 0 else 1.0))
        edge_bonus = 0
        if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
            edge_bonus = 1.1 if (nx, ny) not in opp_terr else 0.0

        score = cell_score + center_score + opp_dist_score + adj_bonus + edge_bonus

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]