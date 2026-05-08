def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    best_dx, best_dy = 0, 0
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in oset:
            continue

        dist = md(nx, ny, ox, oy)
        score = -dist * 1000

        # Small tie-breakers: avoid getting stuck near obstacles, keep pressure toward center.
        if obstacles:
            mind = 10**9
            for (ax, ay) in oset:
                mind = min(mind, md(nx, ny, ax, ay))
            score -= (2 / (mind + 1)) * 10  # closer to obstacles => worse

        # Prefer moves that reduce distance (slight gradient to avoid oscillation).
        score += (md(sx, sy, ox, oy) - dist) * 5

        # Prefer staying closer to opponent's line of movement: reduce both x and y gaps.
        score -= (abs(nx - ox) - abs(sx - ox))**2 * 0.01
        score -= (abs(ny - oy) - abs(sy - oy))**2 * 0.01

        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]