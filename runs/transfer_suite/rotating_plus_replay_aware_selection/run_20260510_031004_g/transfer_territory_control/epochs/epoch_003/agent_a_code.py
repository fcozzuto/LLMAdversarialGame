def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ox, oy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def neigh_count(x, y):
        c = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            if (nx, ny) in opp_terr or (nx, ny) in unclaimed:
                c += 1
        return c

    best_dx, best_dy = 0, 0
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        score = 0.0

        if cell in unclaimed:
            score += 150.0
        if cell in opp_terr:
            score += 220.0  # strong counterclaim
        if cell in self_terr:
            score -= 8.0   # avoid wasting moves unless it helps position

        score += 45.0 * (neigh_count(nx, ny) / 8.0)  # local expansion potential

        # Push toward opponent while not suicidally entering our own territory too much
        d_to_opp = man(nx, ny, px, py)
        score += 30.0 - 2.2 * d_to_opp

        # Discourage getting trapped near obstacles / corners when not attacking
        if (nx, ny) not in opp_terr and cell not in unclaimed:
            bad = 0
            for adx, ady in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ax, ay = nx + adx, ny + ady
                if not inb(ax, ay) or (ax, ay) in obstacles:
                    bad += 1
            score -= 3.5 * bad

        # Tie-break deterministically: prefer diagonal, then toward opponent, then toward lower dx/dy
        if score > best_score + 1e-9:
            best_score, best_dx, best_dy = score, dx, dy
        elif abs(score - best_score) <= 1e-9:
            cand = (0 if (dx == 0 or dy == 0) else 1, -man(nx, ny, px, py), -dx, -dy)
            best_cell = (0 if (best_dx == 0 or best_dy == 0) else 1, -man(ox + best_dx, oy + best_dy, px, py), -best_dx, -best_dy)
            if cand > best_cell:
                best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]