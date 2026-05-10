def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = set(map(tuple, observation.get("resources", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    self_terr = set(map(tuple, observation.get("self_territory", [])))
    opp_terr = set(map(tuple, observation.get("opponent_territory", [])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def neigh8(x, y):
        for dx, dy in dirs:
            if dx == 0 and dy == 0: 
                continue
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    # Prefer boundary expansion to disrupt opponent edge-claiming
    boundary = []
    if opp_terr and unclaimed:
        for ux, uy in unclaimed:
            for nx, ny in neigh8(ux, uy):
                if (nx, ny) in opp_terr:
                    boundary.append((ux, uy))
                    break
    targets = boundary if boundary else list(unclaimed) if unclaimed else list(opp_terr)

    # If no targets, hold position
    if not targets:
        return [0, 0]

    # Choose target closest to us (deterministic)
    tx, ty = min(targets, key=lambda c: (dist(sx, sy, c[0], c[1]), c[0], c[1]))
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0
        # Immediate swing if we step into opponent territory
        if (nx, ny) in opp_terr:
            score += 2000
            score += max(0, 40 - dist(nx, ny, px, py)) * 2
        # Claim value for unclaimed
        if (nx, ny) in unclaimed:
            score += 800
            # Prefer contesting near opponent boundary
            if opp_terr:
                for ax, ay in neigh8(nx, ny):
                    if (ax, ay) in opp_terr:
                        score += 250
                        break
        # Mild preference for consolidating
        if (nx, ny) in self_terr:
            score += 60

        # Resource attraction
        if (nx, ny) in resources:
            score += 120

        # Move toward chosen target
        score += max(0, 50 - dist(nx, ny, tx, ty)) * 3

        # Avoid stepping too close to opponent position unless it flips
        if (nx, ny) not in opp_terr:
            score -= max(0, 8 - dist(nx, ny, px, py)) * 25

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]