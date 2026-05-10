def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    px, py = observation.get("opponent_position", (sx, sy))
    px, py = int(px), int(py)

    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    unclaimed = set(tuple(p) for p in observation.get("unclaimed_cells", []) or [])
    self_terr = set(tuple(p) for p in observation.get("self_territory", []) or [])
    opp_terr = set(tuple(p) for p in observation.get("opponent_territory", []) or [])
    remaining = int(observation.get("remaining_resource_count", 0) or 0)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    best = None
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = 0
        if (nx, ny) in unclaimed:
            score += 100000 if remaining > 0 else 80000
        if (nx, ny) in opp_terr:
            score -= 90000
        if (nx, ny) in self_terr:
            score += 1500
        d_opp = abs(nx - px) + abs(ny - py)
        score += 2000 - 20 * d_opp
        if (nx, ny) == (px, py):
            score -= 5000
        score -= 5 * (abs(nx - sx) + abs(ny - sy))
        if score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best