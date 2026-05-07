def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    moves.sort(key=lambda d: (d[0] * 0 + d[1] * 0, d[0], d[1]))

    best_score = None
    best_move = [0, 0]

    # Evaluate each candidate next cell by best resource "win margin" (opponent distance - self distance),
    # then break ties by closer self distance and then by deterministic move ordering.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        best_margin = -10**9
        best_selfd = 10**9
        for tx, ty in resources:
            self_d = md(nx, ny, tx, ty)
            opp_d = md(ox, oy, tx, ty)
            margin = opp_d - self_d
            if margin > best_margin:
                best_margin = margin
                best_selfd = self_d
            elif margin == best_margin and self_d < best_selfd:
                best_selfd = self_d

        # Prefer positive margins (we arrive earlier), else still minimize self distance.
        score = (best_margin, -best_selfd)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move