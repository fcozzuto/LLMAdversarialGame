def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_cells = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_cells = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves.sort()

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in opp_cells:
            continue

        score = 0
        if (nx, ny) in unclaimed:
            score += 50
        if (nx, ny) in self_cells:
            score += 10

        score -= abs(nx - ox) * 2
        if (dx, dy) != (0, 0):
            score += 1

        # Prefer staying on board if possible, otherwise least bad
        score += 3 if (nx, ny) == (ox, oy) else 0

        # Small deterministic tie-breaker: prefer larger dx,dy order already sorted; add distance to center
        score -= abs(nx - (w - 1) / 2) * 0.01
        score -= abs(ny - (h - 1) / 2) * 0.01

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]