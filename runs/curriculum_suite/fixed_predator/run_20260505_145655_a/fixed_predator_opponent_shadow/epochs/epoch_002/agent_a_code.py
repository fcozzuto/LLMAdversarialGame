def choose_move(observation):
    w = observation.get("grid_width")
    h = observation.get("grid_height")
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles", []):
        try:
            obstacles.add((p[0], p[1]))
        except Exception:
            pass

    resources = []
    for r in observation.get("resources", []):
        try:
            resources.append((r[0], r[1]))
        except Exception:
            pass

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_score = -10**18

    has_res = bool(resources)
    center_x, center_y = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        opp_d = md(nx, ny, ox, oy)
        if has_res:
            dres = min(md(nx, ny, rx, ry) for rx, ry in resources)
            score = 4.0 * opp_d - 1.2 * dres
        else:
            score = 3.5 * opp_d - 0.15 * (abs(nx - center_x) + abs(ny - center_y))

        score += 0.001 * (dx * dx + dy * dy)  # deterministic slight preference
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]