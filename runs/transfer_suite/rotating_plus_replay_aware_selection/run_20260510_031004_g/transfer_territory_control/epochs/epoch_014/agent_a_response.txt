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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = (0, 0)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base: move towards opponent early only if it helps claim/flip
        md_opp = dist(nx, ny, px, py)

        if (nx, ny) in opp_terr:
            score = 100000 - md_opp * 3  # strong flip pressure
        else:
            score = 0
            # Claim expansion
            if (nx, ny) in unclaimed:
                score += 1200
            # Resource pickup
            if (nx, ny) in resources:
                score += 700
            # Avoid wasting on already-owned unless it improves position
            if (nx, ny) in self_terr:
                score -= 40
            # Prefer moving away from opponent while expanding
            score += md_opp * 6
            # Slight tie-break to prefer moves that approach nearest unclaimed cell
            if unclaimed:
                md_un = min(dist(nx, ny, ux, uy) for ux, uy in unclaimed)
                score += -md_un * 2

        # Deterministic tie-break
        key = (score, -dx, -dy, nx, ny, dist(nx, ny, px, py))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]